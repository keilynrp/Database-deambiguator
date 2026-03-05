import numpy as np
from typing import Dict, List, Any

def simulate_citation_impact(current_citations: int, simulation_years: int = 5, num_simulations: int = 5000) -> Dict[str, Any]:
    """
    Monte Carlo Simulation for predictive Scientometrics (Phase 4).
    Simulates the future trajectory of a publication's citation count using a stochastic growth model.
    A Brownian Motion with Drift or Log-Normal model is appropriate for citation diffusion.
    
    Returns:
        A dictionary containing the simulated percentiles (10%, 50%, 90%) for the requested years,
        allowing the UI to draw realistic projection bounds.
    """
    if current_citations <= 0:
         current_citations = 1  # Base assumption to avoid log(0) and allow initial discovery

    # Model parameters (Tuned heuristically for typical scientific halflife and impact decay)
    # The drift (mu) represents expected average annual growth rate in log terms
    # The volatility (sigma) represents variance in discovery/impact outbreaks
    # More established papers (higher current citations) tend to have slightly lower variance but steady drift.
    
    mu_base = 0.15      # 15% average growth
    sigma_base = 0.40   # 40% volatility in citation frequency

    # Decay effect: As citations grow very large, percentage growth naturally slows down 
    # (Law of large numbers / saturation)
    decay_factor = np.clip(1.0 - (np.log1p(current_citations) / 50.0), 0.3, 1.0)
    mu = mu_base * decay_factor
    sigma = sigma_base * decay_factor

    # Allocate memory for simulations: shape = (num_simulations, simulation_years + 1)
    paths = np.zeros((num_simulations, simulation_years + 1))
    paths[:, 0] = current_citations

    # Run stochastic Geometric Brownian Motion paths
    for t in range(1, simulation_years + 1):
        # Generate random normal shocks for this year
        Z = np.random.standard_normal(num_simulations)
        # S_t = S_{t-1} * exp((mu - sigma^2 / 2) + sigma * Z)
        growth_factor = np.exp((mu - (sigma**2) / 2.0) + sigma * Z)
        paths[:, t] = paths[:, t-1] * growth_factor

    paths = np.round(paths).astype(int)

    # Calculate Percentiles (10th - Pessimistic, 50th - Median/Expected, 90th - Optimistic/Viral Impact)
    percentiles_10 = np.percentile(paths, 10, axis=0)
    percentiles_50 = np.percentile(paths, 50, axis=0)
    percentiles_90 = np.percentile(paths, 90, axis=0)

    # Structure data for the Frontend Charting (Recharts)
    timeline = []
    for year in range(simulation_years + 1):
        timeline.append({
            "year": f"Year {year}",
            "optimistic": int(percentiles_90[year]),
            "median": int(percentiles_50[year]),
            "pessimistic": int(percentiles_10[year])
        })

    return {
        "current_citations": current_citations,
        "simulation_years": simulation_years,
        "total_simulations": num_simulations,
        "trajectories": timeline,
        "predicted_5yr_median": int(percentiles_50[-1])
    }
