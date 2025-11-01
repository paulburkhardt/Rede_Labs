from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.schemas.purchase import PurchaseResponse
from app.models.purchase import Purchase
from app.models.product import Product
from app.models.buyer import Buyer
from app.services.phase_manager import ensure_phase, Phase
from app.services.day_manager import get_current_day
from app.services.round_manager import get_current_round

router = APIRouter(prefix="/buy", tags=["purchases"])

# todo: make sure api endpoints only get called if the phase where they are allowed (seller & buyer phase)

@router.post("/{product_id}", response_model=PurchaseResponse)
def create_purchase(
    product_id: str,
    authorization: str = Header(..., description="Bearer token for buyer"),
    db: Session = Depends(get_db)
):
    """
    Simulate a product purchase.
    Customer agents use this endpoint to purchase products.
    Requires Authorization header with buyer token.
    """
    # Extract token from Authorization header
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # Verify buyer exists and token is valid
    buyer = db.query(Buyer).filter(Buyer.auth_token == token).first()
    if not buyer:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    ensure_phase(db, [Phase.BUYER_SHOPPING])
    current_day = get_current_day(db)
    current_round = get_current_round(db)

    # Create purchase record
    db_purchase = Purchase(
        product_id=product_id,
        buyer_id=buyer.id,
        purchased_at=current_day,
        price_of_purchase=product.price_in_cent,
        wholesale_cost_at_purchase=product.wholesale_cost_cents,
        round=current_round,
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    return PurchaseResponse(
        id=db_purchase.id,
        product_id=db_purchase.product_id,
        price_of_purchase=db_purchase.price_of_purchase,
        wholesale_cost_at_purchase=db_purchase.wholesale_cost_at_purchase,
        round=db_purchase.round,
    )


@router.get("/stats/by-seller")
def get_purchases_per_seller(db: Session = Depends(get_db)):
    """
    Get the number of purchases per seller.
    Returns a list of sellers with their purchase counts.
    """
    from app.models.seller import Seller
    
    current_round = get_current_round(db)

    # Query to count purchases per seller
    results = (
        db.query(
            Seller.id,
            func.count(Purchase.id).label("purchase_count")
        )
        .outerjoin(Product, Product.seller_id == Seller.id)
        .outerjoin(
            Purchase,
            and_(
                Purchase.product_id == Product.id,
                Purchase.round == current_round,
            ),
        )
        .group_by(Seller.id)
        .all()
    )
    
    return [
        {
            "seller_id": result.id,
            "purchase_count": result.purchase_count
        }
        for result in results
    ]


@router.get("/stats/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    """
    Provide per-round breakdowns and overall rankings for seller performance.
    """
    from app.models.seller import Seller

    current_round = get_current_round(db)
    sellers = db.query(Seller).all()
    seller_ids = [seller.id for seller in sellers]

    if not seller_ids:
        return {
            "current_round": current_round,
            "rounds": [],
            "overall": {"leaderboard": [], "winners": []},
        }

    purchase_stats = (
        db.query(
            Product.seller_id.label("seller_id"),
            Purchase.round.label("round"),
            func.count(Purchase.id).label("purchase_count"),
            func.coalesce(
                func.sum(
                    Purchase.price_of_purchase - Purchase.wholesale_cost_at_purchase
                ),
                0,
            ).label("total_profit_cents"),
        )
        .join(Product, Purchase.product_id == Product.id)
        .group_by(Product.seller_id, Purchase.round)
        .all()
    )

    all_rounds = {stat.round for stat in purchase_stats}
    all_rounds.add(current_round)
    sorted_rounds = sorted(all_rounds)

    round_stats: dict[int, dict[str, dict[str, int]]] = {
        round_number: {
            seller_id: {"purchase_count": 0, "total_profit_cents": 0}
            for seller_id in seller_ids
        }
        for round_number in sorted_rounds
    }

    for stat in purchase_stats:
        round_data = round_stats.setdefault(
            stat.round,
            {
                seller_id: {"purchase_count": 0, "total_profit_cents": 0}
                for seller_id in seller_ids
            },
        )
        if stat.seller_id not in round_data:
            round_data[stat.seller_id] = {
                "purchase_count": 0,
                "total_profit_cents": 0,
            }

        round_data[stat.seller_id]["purchase_count"] = stat.purchase_count
        round_data[stat.seller_id]["total_profit_cents"] = stat.total_profit_cents

    overall_stats: dict[str, dict[str, int]] = {
        seller_id: {
            "purchase_count": 0,
            "total_profit_cents": 0,
            "round_wins": 0,
        }
        for seller_id in seller_ids
    }

    rounds_payload = []
    for round_number in sorted_rounds:
        sellers_for_round = round_stats[round_number]
        entries = []
        for seller_id, stats in sellers_for_round.items():
            overall_record = overall_stats.setdefault(
                seller_id,
                {
                    "purchase_count": 0,
                    "total_profit_cents": 0,
                    "round_wins": 0,
                },
            )
            overall_record["purchase_count"] += stats["purchase_count"]
            overall_record["total_profit_cents"] += stats["total_profit_cents"]

            entries.append(
                {
                    "seller_id": seller_id,
                    "purchase_count": stats["purchase_count"],
                    "total_profit_cents": stats["total_profit_cents"],
                    "total_profit_dollars": stats["total_profit_cents"] / 100.0,
                }
            )

        entries.sort(
            key=lambda entry: (
                -entry["total_profit_cents"],
                -entry["purchase_count"],
                entry["seller_id"],
            )
        )

        round_has_activity = any(
            entry["purchase_count"] > 0 for entry in entries
        )
        if round_has_activity:
            highest_profit = entries[0]["total_profit_cents"]
            winners = [
                entry["seller_id"]
                for entry in entries
                if entry["total_profit_cents"] == highest_profit
            ]
            for winner in winners:
                overall_stats[winner]["round_wins"] += 1
        else:
            winners = []

        rounds_payload.append(
            {
                "round": round_number,
                "is_current_round": round_number == current_round,
                "leaderboard": entries,
                "winners": winners,
            }
        )

    overall_leaderboard = [
        {
            "seller_id": seller_id,
            "purchase_count": stats["purchase_count"],
            "total_profit_cents": stats["total_profit_cents"],
            "total_profit_dollars": stats["total_profit_cents"] / 100.0,
            "round_wins": stats["round_wins"],
        }
        for seller_id, stats in overall_stats.items()
    ]
    overall_leaderboard.sort(
        key=lambda entry: (
            -entry["round_wins"],
            -entry["total_profit_cents"],
            -entry["purchase_count"],
            entry["seller_id"],
        )
    )

    overall_winners = []
    if overall_leaderboard:
        max_wins = overall_leaderboard[0]["round_wins"]
        overall_winners = [
            entry["seller_id"]
            for entry in overall_leaderboard
            if entry["round_wins"] == max_wins
        ]

    return {
        "current_round": current_round,
        "rounds": rounds_payload,
        "overall": {
            "leaderboard": overall_leaderboard,
            "winners": overall_winners,
        },
    }
