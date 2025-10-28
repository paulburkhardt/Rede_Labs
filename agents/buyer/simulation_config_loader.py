"""
Customer Simulation Configuration Loader

This module provides utilities to load and work with customer simulation
configuration, including persona distribution and customer counts.
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
            # Default to the agents directory
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
    
    @property
    def customers_per_run(self) -> int:
        """Get number of customers to simulate per run."""
        return self.config["simulation_settings"]["customers_per_run"]
    
    @property
    def random_seed(self) -> int | None:
        """Get random seed for reproducible simulations."""
        return self.config["simulation_settings"].get("random_seed")
    
    @property
    def use_weighted_sampling(self) -> bool:
        """Check if weighted sampling should be used."""
        return self.config["simulation_settings"]["use_weighted_sampling"]
    
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
    
    def sample_customers(self, n: int = None) -> List[str]:
        """
        Sample customer personas for a simulation run.
        
        Args:
            n: Number of customers to sample. If None, uses customers_per_run from config.
            
        Returns:
            List of persona IDs representing sampled customers
        """
        if n is None:
            n = self.customers_per_run
        
        # Set random seed if specified
        if self.random_seed is not None:
            random.seed(self.random_seed)
        
        if self.use_weighted_sampling:
            # Weighted random sampling based on distribution
            personas = list(self.persona_distribution.keys())
            weights = list(self.persona_distribution.values())
            return random.choices(personas, weights=weights, k=n)
        else:
            # Proportional sampling (maintain exact distribution)
            return self._proportional_sample(n)
    
    def _proportional_sample(self, n: int) -> List[str]:
        """
        Sample customers maintaining exact proportions.
        
        Args:
            n: Number of customers to sample
            
        Returns:
            List of persona IDs with exact proportions
        """
        sample = []
        remaining = n
        
        personas = list(self.persona_distribution.items())
        for i, (persona_id, percentage) in enumerate(personas):
            if i == len(personas) - 1:
                # Last persona gets remaining slots
                count = remaining
            else:
                count = int(n * (percentage / 100.0))
                remaining -= count
            
            sample.extend([persona_id] * count)
        
        # Shuffle to randomize order
        random.shuffle(sample)
        return sample
    
    def get_summary(self) -> Dict:
        """
        Get a summary of the simulation configuration.
        
        Returns:
            Dictionary with configuration summary
        """
        counts = self.get_persona_counts()
        
        return {
            "total_customers": self.total_customers,
            "customers_per_run": self.customers_per_run,
            "persona_distribution": self.persona_distribution,
            "persona_counts": counts,
            "random_seed": self.random_seed,
            "use_weighted_sampling": self.use_weighted_sampling
        }
    
    def print_summary(self):
        """Print a formatted summary of the configuration."""
        summary = self.get_summary()
        counts = summary["persona_counts"]
        
        print("=" * 60)
        print("CUSTOMER SIMULATION CONFIGURATION")
        print("=" * 60)
        print(f"\nTotal Customers: {summary['total_customers']:,}")
        print(f"Customers per Run: {summary['customers_per_run']:,}")
        print(f"Random Seed: {summary['random_seed']}")
        print(f"Weighted Sampling: {summary['use_weighted_sampling']}")
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

