# AI Resume Screener
1. `pip install -r requirements.txt`
2. `python -m spacy download en_core_web_sm`
3. Place `UpdatedResumeDataset.csv` inside the `data/` folder.
4. `python train_model.py` (trains SVM, saves model files)
5. `python app.py` (starts the Flask server)

Default admin login:
Email: admin@gmail.com | Password: Admin@1234