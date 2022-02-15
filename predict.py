from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from function import pre_process_features, BuildDataset
from transformers import Trainer
def prediction_data(data):

    tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", use_fast=False)
    model = AutoModelForSequenceClassification.from_pretrained("model")
    trainer = Trainer(model=model)
    X_test = list(data.comment)
    y_test = []
    for i in range(len(X_test)):
        y_test.append(0)
    test_X, test_y = pre_process_features(X_test, y_test, tokenized=True, lowercased = True)
    test_encodings = tokenizer(test_X, truncation=True, padding=True, max_length=200)
    test_dataset = BuildDataset(test_encodings, test_y)
    y_pred_classify_2 = trainer.predict(test_dataset)
    y_pred = np.argmax(y_pred_classify_2.predictions, axis=-1)
    return y_pred
