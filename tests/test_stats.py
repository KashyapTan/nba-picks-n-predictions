"""
Test script for NBA stats functions
"""

from formula import get_player_season_stats, get_player_vs_team_stats


def print_stats(stats, title):
    """Helper function to print stats nicely"""
    print(f"\n{title}")
    print("=" * 60)
    print(f"Games Played: {stats['games_played']}")
    print(f"\nAverages (± Standard Deviation):")
    print(f"  Points:   {stats['averages']['points']:6.1f} ± {stats['std_devs']['points']:.1f}")
    print(f"  Rebounds: {stats['averages']['rebounds']:6.1f} ± {stats['std_devs']['rebounds']:.1f}")
    print(f"  Assists:  {stats['averages']['assists']:6.1f} ± {stats['std_devs']['assists']:.1f}")
    print(f"  Blocks:   {stats['averages']['blocks']:6.1f} ± {stats['std_devs']['blocks']:.1f}")
    print(f"  Steals:   {stats['averages']['steals']:6.1f} ± {stats['std_devs']['steals']:.1f}")


def main():
    print("NBA PLAYER STATISTICS ANALYZER")
    print("=" * 60)
    
    # Test 1: Season stats for a player
    try:
        player = "Nikola Jokic"
        season = "2023-24"
        print(f"\nFetching {player}'s stats for {season} season...")
        stats = get_player_season_stats(player, season)
        print_stats(stats, f"{player} - {season} Regular Season")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Another player's season stats
    try:
        player = "Giannis Antetokounmpo"
        season = "2023-24"
        print(f"\nFetching {player}'s stats for {season} season...")
        stats = get_player_season_stats(player, season)
        print_stats(stats, f"{player} - {season} Regular Season")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Stats vs specific team
    try:
        player = "Stephen Curry"
        season = "2023-24"
        opponent = "Lakers"
        print(f"\nFetching {player}'s stats vs {opponent} in {season}...")
        stats = get_player_vs_team_stats(player, season, opponent)
        print_stats(stats, f"{player} vs {opponent} - {season}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Stats vs specific team (using abbreviation)
    try:
        player = "Kevin Durant"
        season = "2023-24"
        opponent = "GSW"  # Using abbreviation
        print(f"\nFetching {player}'s stats vs {opponent} in {season}...")
        stats = get_player_vs_team_stats(player, season, opponent)
        print_stats(stats, f"{player} vs Golden State Warriors - {season}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")


if __name__ == "__main__":
    main()
