"""
Test and demonstration script for NBA percentile analysis functions
"""

from percentile import (
    get_player_percentiles_season,
    plot_player_percentiles_season,
    get_player_percentiles_vs_team,
    plot_player_percentiles_vs_team
)


def demo_season_percentiles():
    """Demonstrate season percentile analysis"""
    print("=" * 80)
    print("DEMO 1: Season Percentile Analysis")
    print("=" * 80)
    
    player = "Nikola Jokic"
    season = "2023-24"
    
    print(f"\nAnalyzing {player} for the {season} season...")
    
    # Get percentile data
    data = get_player_percentiles_season(player, season)
    
    print(f"\n{player} - {season} Season Statistics")
    print("-" * 80)
    print(f"Games Played: {data['games_played']}")
    
    # Display percentiles
    print("\nPercentile Breakdown:")
    print(f"{'Stat':<12} {'25th':<8} {'50th':<8} {'75th':<8} {'Max':<8}")
    print("-" * 50)
    
    for stat in ['points', 'rebounds', 'assists', 'blocks', 'steals']:
        p = data['percentiles'][stat]
        print(f"{stat.capitalize():<12} {p['25th']:<8.1f} {p['50th']:<8.1f} "
              f"{p['75th']:<8.1f} {p['100th']:<8.1f}")
    
    # Create visualization
    print(f"\nGenerating box plot visualization...")
    plot_player_percentiles_season(player, season, 
                                   save_path=f"{player.replace(' ', '_')}_season.png")
    print(f"✓ Saved visualization to {player.replace(' ', '_')}_season.png")


def demo_vs_team_percentiles():
    """Demonstrate vs team percentile analysis"""
    print("\n" + "=" * 80)
    print("DEMO 2: Percentile Analysis vs Specific Team")
    print("=" * 80)
    
    player = "Kevin Durant"
    season = "2023-24"
    opponent = "Celtics"
    
    print(f"\nAnalyzing {player} vs {opponent} for the {season} season...")
    
    # Get percentile data
    data = get_player_percentiles_vs_team(player, season, opponent)
    
    print(f"\n{player} vs {data['opponent']} - {season}")
    print("-" * 80)
    print(f"Games Played: {data['games_played']}")
    
    # Display percentiles
    print("\nPercentile Breakdown:")
    print(f"{'Stat':<12} {'25th':<8} {'50th':<8} {'75th':<8} {'Max':<8}")
    print("-" * 50)
    
    for stat in ['points', 'rebounds', 'assists', 'blocks', 'steals']:
        p = data['percentiles'][stat]
        print(f"{stat.capitalize():<12} {p['25th']:<8.1f} {p['50th']:<8.1f} "
              f"{p['75th']:<8.1f} {p['100th']:<8.1f}")
    
    # Create visualization
    print(f"\nGenerating box plot visualization...")
    plot_player_percentiles_vs_team(player, season, opponent,
                                    save_path=f"{player.replace(' ', '_')}_vs_{opponent}.png")
    print(f"✓ Saved visualization to {player.replace(' ', '_')}_vs_{opponent}.png")


def compare_multiple_players():
    """Compare percentiles across multiple players"""
    print("\n" + "=" * 80)
    print("DEMO 3: Comparing Multiple Players")
    print("=" * 80)
    
    players = ["Stephen Curry", "Damian Lillard", "Kyrie Irving"]
    season = "2023-24"
    
    print(f"\nComparing point guards for {season} season:")
    print("\nPoints - 50th Percentile (Median) Comparison:")
    print("-" * 50)
    
    for player in players:
        try:
            data = get_player_percentiles_season(player, season)
            median_pts = data['percentiles']['points']['50th']
            games = data['games_played']
            print(f"{player:<20} {median_pts:>6.1f} pts  ({games} games)")
            
            # Save individual plots
            plot_player_percentiles_season(
                player, season, 
                save_path=f"{player.replace(' ', '_')}_comparison.png"
            )
        except Exception as e:
            print(f"{player:<20} Error: {e}")
    
    print(f"\n✓ Individual plots saved for each player")


def advanced_analysis():
    """Show advanced analysis using the percentile data"""
    print("\n" + "=" * 80)
    print("DEMO 4: Advanced Statistical Analysis")
    print("=" * 80)
    
    player = "Giannis Antetokounmpo"
    season = "2023-24"
    
    data = get_player_percentiles_season(player, season)
    
    print(f"\n{player} - {season} Advanced Metrics")
    print("-" * 80)
    
    # Calculate interquartile range (IQR) for consistency measure
    print("\nConsistency Analysis (smaller IQR = more consistent):")
    print(f"{'Stat':<12} {'IQR':<10} {'Interpretation'}")
    print("-" * 60)
    
    for stat in ['points', 'rebounds', 'assists']:
        p = data['percentiles'][stat]
        iqr = p['75th'] - p['25th']
        
        if stat == 'points':
            consistency = "Very consistent" if iqr < 10 else "Moderate variance" if iqr < 15 else "High variance"
        else:
            consistency = "Very consistent" if iqr < 3 else "Moderate variance" if iqr < 5 else "High variance"
        
        print(f"{stat.capitalize():<12} {iqr:<10.1f} {consistency}")
    
    # Show high performance games
    print("\nHigh Performance Analysis:")
    print(f"{'Stat':<12} {'75th %ile':<12} {'Max':<12} {'Max/75th Ratio'}")
    print("-" * 60)
    
    for stat in ['points', 'rebounds', 'assists']:
        p = data['percentiles'][stat]
        ratio = p['100th'] / p['75th'] if p['75th'] > 0 else 0
        print(f"{stat.capitalize():<12} {p['75th']:<12.1f} {p['100th']:<12.1f} {ratio:<.2f}x")
    
    # Generate plot
    plot_player_percentiles_season(player, season,
                                   save_path=f"{player.replace(' ', '_')}_advanced.png")
    print(f"\n✓ Visualization saved")


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "NBA PERCENTILE ANALYSIS DEMOS" + " " * 29 + "║")
    print("╚" + "═" * 78 + "╝")
    
    try:
        # Run demonstrations
        demo_season_percentiles()
        demo_vs_team_percentiles()
        compare_multiple_players()
        advanced_analysis()
        
        print("\n" + "=" * 80)
        print("All demonstrations completed successfully!")
        print("=" * 80)
        print("\nGenerated visualizations:")
        print("  - Individual player season statistics (box plots)")
        print("  - Player vs team statistics (box plots)")
        print("  - Comparison plots for multiple players")
        print("\nBox plots show:")
        print("  • 25th, 50th (median), 75th, and 100th (max) percentiles")
        print("  • All individual game values as scatter points")
        print("  • Visual representation of consistency and variability")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nError during demo: {e}")


if __name__ == "__main__":
    main()
