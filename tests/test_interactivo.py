import demo_interactivo as di


def run(inputs):
    it = iter(inputs)
    lines = []
    def fake_input(prompt=""):
        lines.append(prompt)
        try:
            return next(it)
        except StopIteration:
            raise EOFError
    out = []
    di.main([], input_fn=fake_input, out=out.append, live=False)
    return "\n".join(out)


def test_change_parameters_and_exit():
    text = run(["1", "2", "20", "0.5", "3", "n", "0"])
    assert "m = 32" in text or "k=2 (m=32)" in text
    assert "ruido=no" in text


def test_run_all_shows_every_algorithm():
    text = run(["1", "2", "20", "0.5", "3", "s", "3", "0"])
    for name in ("Backtracking sin poda", "Backtracking con poda", "Successive Halving",
                 "Coordinate Search", "Reparto uniforme", "Reparto adaptativo"):
        assert name in text


def test_single_algorithm_runs():
    text = run(["1", "2", "20", "0.5", "3", "s", "2", "2", "0"])
    assert "consultas" in text and "Backtracking con poda" in text


def test_step_by_step_shows_pruning_and_can_continue():
    text = run(["1", "2", "20", "0.5", "3", "n", "4", "c", "0"])
    assert "PODA" in text and "HOJA" in text and "Resultado" in text


def test_step_by_step_can_abort():
    text = run(["1", "2", "20", "0.5", "3", "n", "4", "q", "0"])
    assert "interrumpido" in text.lower()


def test_multi_seed_average():
    text = run(["1", "2", "20", "0.5", "3", "n", "5", "4", "0"])
    assert "regret medio" in text.lower()


def test_invalid_input_reprompts_and_eof_exits():
    text = run(["x", "9", "0"])
    assert "opcion no valida" in text.lower()
    run(["3"])  # EOF a mitad: no debe lanzar excepcion
