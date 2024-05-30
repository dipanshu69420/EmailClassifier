from transformers import AutoTokenizer, AutoModelForSequenceClassification

class predict_class:
    def __init__(self, model_path, tokenizer_path):
        self.model = AutoModelForSequenceClassification.from_pretrained(r"D:\EmailClassify\EmailClassifier\classification-params")
        self.tokenizer = AutoTokenizer.from_pretrained(r"D:\EmailClassify\EmailClassifier\classification-params")

        self.model1=AutoModelForSequenceClassification.from_pretrained(r"D:\EmailClassify\EmailClassifier\priority-params")
        self.tokenizer1=AutoTokenizer.from_pretrained(r"D:\EmailClassify\EmailClassifier\priority-params")

        self.model2 = AutoModelForSequenceClassification.from_pretrained(r"D:\EmailClassify\EmailClassifier\escalation-params")
        self.tokenizer2 = AutoTokenizer.from_pretrained(r"D:\EmailClassify\EmailClassifier\escalation-params")

    def classify(self, text):
        inputs = self.tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
        outputs = self.model(**inputs)
        probs = outputs[0].softmax(1)
        pred_label_idx = probs.argmax()
        pred_label = self.model.config.id2label[pred_label_idx.item()]
        return pred_label

    def prioritize(self, text):
        inputs = self.tokenizer1(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
        outputs = self.model1(**inputs)
        probs = outputs[0].softmax(1)
        pred_label_idx = probs.argmax()
        pred_label = self.model1.config.id2label[pred_label_idx.item()]
        return pred_label

    def escalation(self, text):
        inputs = self.tokenizer2(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
        outputs = self.model2(**inputs)
        probs = outputs[0].softmax(1)
        pred_label_idx = probs.argmax()
        pred_label = self.model2.config.id2label[pred_label_idx.item()]
        return pred_label



