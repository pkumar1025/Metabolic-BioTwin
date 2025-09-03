run:
	uvicorn app.main:app --reload

demo:
	python scripts/generate_synthetic.py
