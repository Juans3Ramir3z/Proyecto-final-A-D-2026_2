import demo


def test_demo_prints_all_algorithms(capsys):
    demo.main(["--k", "2", "--n", "20", "--rho", "0.5", "--seed", "3"])
    out = capsys.readouterr().out
    for name in ("Backtracking sin poda", "Backtracking con poda", "Successive Halving",
                 "Coordinate Search", "Reparto uniforme", "Reparto adaptativo"):
        assert name in out
    assert "m = 32" in out


def test_demo_no_prune_costs_m_times_N(capsys):
    demo.main(["--k", "2", "--n", "20"])
    line = [l for l in capsys.readouterr().out.splitlines() if l.startswith("Backtracking sin poda")][0]
    assert "640" in line  # 32 * 20
