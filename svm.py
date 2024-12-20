# -*- coding: utf-8 -*-
"""svm.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zdVHhYPNZlymCo_cr0_JWG9izdyHqXEx
"""

!pip install pycm==0.8.1

import kagglehub

# Download latest version
path = kagglehub.dataset_download("andradaolteanu/gtzan-dataset-music-genre-classification")

print("Path to dataset files:", path)



import os

# Define the dataset path
dataset_path = "/root/.cache/kagglehub/datasets/andradaolteanu/gtzan-dataset-music-genre-classification/versions/1"

# Walk through the directory and print its structure
for root, dirs, files in os.walk(dataset_path):
    print(f"Root: {root}")
    print(f"Dirs: {dirs}")
    print(f"Files: {files}")



import os
import librosa
import numpy as np
import pickle

# Define the path to the GTZAN dataset
dataset_path = "/root/.cache/kagglehub/datasets/andradaolteanu/gtzan-dataset-music-genre-classification/versions/1/Data/genres_original"

# Function to extract Mel Spectrogram features
def extractMelSpectrogram_features_gtzan(folder):
    hop_length = 512
    n_fft = 2048
    n_mels = 128
    genres = ["blues", "classical", "country", "disco", "hiphop", "jazz", "metal", "pop", "reggae", "rock"]

    features = []
    labels = []

    # Iterate directly through genre folders within the dataset_path
    for genre in genres:
        genre_path = os.path.join(folder, genre)
        if not os.path.isdir(genre_path):
            print(f"Warning: Genre folder not found: {genre_path}")
            continue

        for filename in os.listdir(genre_path):
            if filename.endswith(".wav"):
                file_path = os.path.join(genre_path, filename)
                print(f"Processing file: {file_path}")
                try:
                    signal, rate = librosa.load(file_path)
                    S = librosa.feature.melspectrogram(y=signal, sr=rate, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels)
                    S_DB = librosa.power_to_db(S, ref=np.max)
                    S_DB = S_DB.flatten()[:1200]  # Flatten and truncate to fixed length
                    features.append(S_DB)
                    labels.append(genres.index(genre))  # Assign a numeric label for each genre
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    # Reshape features to 2D array if not empty
    if features:
        features = np.array(features)  # Convert features list to a numpy array
        if features.ndim == 1:  # Check if features is 1D
            features = features.reshape(-1, 1)  # Reshape to 2D if it is 1D
    else:
        print("Warning: No features extracted. Check dataset path and file format.")  # Print a warning if no features are extracted

    return features, labels


# Extract features and labels from the GTZAN dataset
features, labels = extractMelSpectrogram_features_gtzan(dataset_path)

# Save the features and labels to pickle files
save_dir = ""
# os.makedirs(save_dir, exist_ok=True)  # Avoid errors if the directory exists

pickle.dump(features, open(save_dir+'mel_features_gtzan.data', 'wb'))
pickle.dump(labels, open(save_dir+'mel_labels_gtzan.data', 'wb'))

import numpy as np
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from pycm import ConfusionMatrix
import pickle
import os  # Import the os module

# Load the features and labels from pickle
features = pickle.load(open(save_dir+'mel_features_gtzan.data', 'rb'))
labels = pickle.load(open(save_dir+'mel_labels_gtzan.data', 'rb'))

# Check the shape of features and labels
print(f"Features shape: {np.shape(features)}")
print(f"Labels shape: {np.shape(labels)}")

# Ensure features is a 2D array (samples, features)
features = np.array(features)
if len(features.shape) == 1:
    features = features.reshape(-1, 1)  # Reshape to 2D if needed

# Ensure labels is a 1D array
labels = np.array(labels).flatten()

# Train the SVM classifier
clf = SVC(kernel="rbf")
clf.fit(features, labels)

# Test the model with the same data (or separate test data if available)
list_y_true = labels
list_y_pred = clf.predict(features)

# Generate a classification report
print(classification_report(list_y_true, list_y_pred, target_names=["blues", "classical", "country", "disco", "hiphop", "jazz", "metal", "pop", "reggae", "rock"]))

# Save the confusion matrix report
results = "/content/drive/MyDrive/ourdataset/results/report.txt"

# Create the directory if it doesn't exist
os.makedirs(os.path.dirname(results), exist_ok=True)

with open(results, "w") as f:
    cm = ConfusionMatrix(actual_vector=list_y_true, predict_vector=list_y_pred)
    f.write(f"{cm}\n")

def predict_genre(file_path, clf):
    # Load and preprocess the audio file
    signal, rate = librosa.load(file_path)
    hop_length = 512
    n_fft = 2048
    n_mels = 128
    S = librosa.feature.melspectrogram(y=signal, sr=rate, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels)
    S_DB = librosa.power_to_db(S, ref=np.max)
    S_DB = S_DB.flatten()[:1200]

    # Predict the genre
    genre_label = clf.predict([S_DB])[0]
    genres = ["blues", "classical", "country", "disco", "hiphop", "jazz", "metal", "pop", "reggae", "rock"]
    return genres[genre_label]

# Test prediction on a new file
file_path = "/root/.cache/kagglehub/datasets/andradaolteanu/gtzan-dataset-music-genre-classification/versions/1/Data/genres_original/country/country.00002.wav"
predicted_genre = predict_genre(file_path, clf)
print(f"The predicted genre is: {predicted_genre}")

# Save the trained model to a file
with open('svm_model.pkl', 'wb') as model_file:
    pickle.dump(clf, model_file)