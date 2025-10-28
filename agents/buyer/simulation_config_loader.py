"""
Customer Simulation Configuration Loader

Simple utility to load customer population and persona distribution.
"""

import random
from pathlib import Path
from typing import Dict, List
import toml


class SimulationConfig:
    """Manages customer simulation configuration."""
    
    def __init__(self, config_path: str = None):
        """
        Load simulation configuration from TOML file.
        
        Args:
            config_path: Path to simulation_config.toml. If None, uses default location.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "simulation_config.toml"
        
        self.config = toml.load(config_path)
        self._validate_config()
        
    def _validate_config(self):
        """Validate that persona distribution sums to 100%."""
        distribution = self.config["persona_distribution"]
        total = sum(distribution.values())
        
        if not (99.9 <= total <= 100.1):  # Allow for floating point imprecision
            raise ValueError(
                f"Persona distribution must sum to 100%, got {total}%. "
                f"Current distribution: {distribution}"
            )
    
    @property
    def total_customers(self) -> int:
        """Get total number of customers in the simulation."""
        return self.config["customer_population"]["total_customers"]
    
    @property
    def persona_distribution(self) -> Dict[str, float]:
        """Get persona distribution percentages."""
        return self.config["persona_distribution"]
    
    def get_persona_counts(self) -> Dict[str, int]:
        """
        Calculate absolute customer counts for each persona based on distribution.
        
        Returns:
            Dictionary mapping persona_id to customer count
        """
        counts = {}
        remaining = self.total_customers
        
        # Calculate counts for each persona
        personas = list(self.persona_distribution.items())
        for i, (persona_id, percentage) in enumerate(personas):
            if i == len(personas) - 1:
                # Last persona gets remaining customers to avoid rounding errors
                counts[persona_id] = remaining
            else:
                count = int(self.total_customers * (percentage / 100.0))
                counts[persona_id] = count
                remaining -= count
        
        return counts
    
    def sample_customers(self, n: int) -> List[str]:
        """
        Sample customer personas using weighted random sampling.
        
        Args:
            n: Number of customers to sample
            
        Returns:
            List of persona IDs representing sampled customers
        """
        personas = list(self.persona_distribution.keys())
        weights = list(self.persona_distribution.values())
        return random.choices(personas, weights=weights, k=n)
    
    def get_summary(self) -> Dict:
        """
        Get a summary of the simulation configuration.
        
        Returns:
            Dictionary with configuration summary
        """
        counts = self.get_persona_counts()
        
        return {
            "total_customers": self.total_customers,
            "persona_distribution": self.persona_distribution,
            "persona_counts": counts
        }
    
    def print_summary(self):
        """Print a formatted summary of the configuration."""
        summary = self.get_summary()
        counts = summary["persona_counts"]
        
        print("=" * 60)
        print("CUSTOMER SIMULATION CONFIGURATION")
        print("=" * 60)
        print(f"\nTotal Customers: {summary['total_customers']:,}")
        print("\n" + "-" * 60)
        print("PERSONA DISTRIBUTION")
        print("-" * 60)
        
        for persona_id, percentage in summary["persona_distribution"].items():
            count = counts[persona_id]
            print(f"{persona_id:25} {percentage:5.1f}%  ({count:,} customers)")
        
        print("=" * 60)


# Convenience function for quick access
def load_simulation_config(config_path: str = None) -> SimulationConfig:
    """
    Load simulation configuration.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        SimulationConfig instance
    """
    return SimulationConfig(config_path)


# Example usage
if __name__ == "__main__":
    # Load and display configuration
    config = load_simulation_config()
    config.print_summary()
    
    print("\n" + "=" * 60)
    print("SAMPLE RUN (100 customers)")
    print("=" * 60)
    
    # Sample 100 customers
    sample = config.sample_customers(100)
    
    # Count distribution in sample
    from collections import Counter
    sample_counts = Counter(sample)
    
    for persona_id, count in sorted(sample_counts.items()):
        percentage = (count / len(sample)) * 100
        print(f"{persona_id:25} {count:3} customers ({percentage:.1f}%)")
