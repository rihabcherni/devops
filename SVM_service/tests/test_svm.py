import unittest
import base64
import json
from app import app
from io import BytesIO
import xmlrunner


class TestSVMService(unittest.TestCase): 
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_predict_svm_valid_audio(self):
        with open("tests/test_audio.wav", "rb") as f:
            audio_data = f.read()
        base64_audio = base64.b64encode(audio_data).decode('utf-8')
        
        response = self.client.post(
            '/predict_svm',
            data=json.dumps({'wav_music': base64_audio}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('genre', data)  
        self.assertIn(data['genre'], ["blues", "classical", "country", "disco", 
                                      "hiphop", "jazz", "metal", "pop", "reggae", "rock"])
    

    def test_predict_svm_no_audio(self):
        response = self.client.post(
            '/predict_svm',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Aucun fichier audio fourni')

    def test_predict_svm_invalid_audio(self):
        # Envoyer des données non valides
        response = self.client.post(
            '/predict_svm',
            data=json.dumps({'wav_music': 'invalid_base64'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_svm_service_error_handling(self):
        # Simuler un cas où une exception interne se produit
        with app.test_request_context('/predict_svm', method='POST'):
            response = self.client.post(
                '/predict_svm',
                data=json.dumps({'wav_music': base64.b64encode(b"invalid data").decode()}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertIn('error', data)

if __name__ == "__main__":
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='/reports'),
        failfast=False,
        buffer=False,
        catchbreak=False,
    )
