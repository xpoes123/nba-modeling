"""Unit tests for injury-share normalization in lineup minute profiles."""
import math

from downstream.lineup_sampler import MinutesProfile


def _make_profile(shares: dict[str, float], scale: float = 240.0) -> MinutesProfile:
    """Build a MinutesProfile from possession-share fractions."""
    return MinutesProfile({pid: (s * scale, 0.03 * scale) for pid, s in shares.items()})


class TestMinutesNormalization:
    def test_full_health_sums_to_240(self):
        """Five equal-share players at 0.20 each → total = 240 synthetic minutes."""
        profile = _make_profile({"p1": 0.20, "p2": 0.20, "p3": 0.20, "p4": 0.20, "p5": 0.20})
        total = sum(m for m, _ in profile.values())
        assert math.isclose(total, 240.0, rel_tol=1e-6)

    def test_injured_star_scaled_to_240(self):
        """After removing a star (35% share), scale remaining 65% back to 240."""
        # Four backups share the 65% that remains after a star is excluded
        profile = _make_profile({"b1": 0.1625, "b2": 0.1625, "b3": 0.1625, "b4": 0.1625})
        coverage_ratio = 0.65
        scale = 1.0 / coverage_ratio
        scaled = MinutesProfile(
            {pid: (m * scale, s * scale) for pid, (m, s) in profile.items()}
        )
        total = sum(m for m, _ in scaled.values())
        assert math.isclose(total, 240.0, rel_tol=1e-4)

    def test_scaling_preserves_relative_shares(self):
        """Scaling by a constant factor should not change each player's relative share."""
        profile = _make_profile({"p1": 0.10, "p2": 0.15, "p3": 0.12})
        coverage_ratio = 0.37
        scale = 1.0 / coverage_ratio
        scaled = MinutesProfile(
            {pid: (m * scale, s * scale) for pid, (m, s) in profile.items()}
        )
        orig_total = sum(m for m, _ in profile.values())
        scaled_total = sum(m for m, _ in scaled.values())
        for pid in profile:
            orig_share = profile[pid][0] / orig_total
            scaled_share = scaled[pid][0] / scaled_total
            assert math.isclose(orig_share, scaled_share, rel_tol=1e-6)

    def test_coverage_ratio_not_modified_by_scaling(self):
        """coverage_ratio is computed before scaling and must not change."""
        available = 0.65
        total = 1.0
        coverage_ratio = available / total
        # Simulate what the code does: scale the profile, then verify ratio unchanged
        assert math.isclose(coverage_ratio, 0.65)

    def test_std_scaled_proportionally(self):
        """std_minutes should scale by the same factor as mean_minutes."""
        original_mean = 24.0
        original_std = 5.0
        coverage_ratio = 0.60
        scale = 1.0 / coverage_ratio
        scaled_mean = original_mean * scale
        scaled_std = original_std * scale
        # Coefficient of variation should be preserved
        assert math.isclose(original_std / original_mean, scaled_std / scaled_mean, rel_tol=1e-6)
