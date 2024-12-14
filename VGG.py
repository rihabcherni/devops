# -*- coding: utf-8 -*-
"""lastVGG.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1BS2bOKgVZlzwCe2IrFuYw-RDkfkf3XoN
"""

import kagglehub

# Download latest version
path = kagglehub.dataset_download("andradaolteanu/gtzan-dataset-music-genre-classification")

print("Path to dataset files:", path)

pip install tensorflow librosa numpy matplotlib scikit-learn

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

    # Iterate through genre folders within the dataset_path
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
    else:
        print("Warning: No features extracted. Check dataset path and file format.")

    return features, labels

# Extract features and labels from the GTZAN dataset
features, labels = extractMelSpectrogram_features_gtzan(dataset_path)

# Save the features and labels to pickle files
save_dir = "/content/"
pickle.dump(features, open(save_dir + 'mel_features_gtzan.data', 'wb'))
pickle.dump(labels, open(save_dir + 'mel_labels_gtzan.data', 'wb'))

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Flatten, Dropout
from tensorflow.keras.applications import VGG19
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import pickle
import numpy as np

# Load features and labels
features = pickle.load(open(save_dir + 'mel_features_gtzan.data', 'rb'))
labels = pickle.load(open(save_dir + 'mel_labels_gtzan.data', 'rb'))

# Normalize features (optional but recommended)
features = features / np.max(features)

# Convert labels to categorical (one-hot encoding)
labels = to_categorical(labels, num_classes=10)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# Reshape the data to be compatible with VGG19 input (adding a channel dimension)
X_train = X_train.reshape(X_train.shape[0], 40, 30, 1)
X_test = X_test.reshape(X_test.shape[0], 40, 30, 1)

# Resize images to meet the minimum size requirement for VGG19 (32x32)
X_train_resized = tf.image.resize(X_train, (32, 32))
X_test_resized = tf.image.resize(X_test, (32, 32))

# Convert back to 3 channels if necessary (as VGG19 expects 3 channels)
X_train_resized = tf.repeat(X_train_resized, 3, axis=-1)
X_test_resized = tf.repeat(X_test_resized, 3, axis=-1)

# Build the VGG19 model
base_model = VGG19(weights="imagenet", include_top=False, input_shape=(32, 32, 3))  # Use 32x32 input size

# Freeze the base model to prevent training its weights
base_model.trainable = False

# Add custom layers on top of VGG19
x = Flatten()(base_model.output)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)  # Dropout to prevent overfitting
x = Dense(10, activation='softmax')(x)  # 10 output classes for 10 genres

# Define the complete model
model = Model(inputs=base_model.input, outputs=x)

# Compile the model
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

# Train the model
history = model.fit(X_train_resized, y_train, epochs=10, batch_size=32, validation_data=(X_test_resized, y_test))

# Save the model to a file
model.save('/content/music_genre_vgg19_model.keras')

print(X_train.shape)
print(X_test.shape)

import numpy as np
import librosa

# Evaluate the model on the test set
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {test_acc:.4f}")

# Predict the genre of a new file
def predict_genre_vgg19(file_path, model):
    signal, rate = librosa.load(file_path, sr=None)  # Load audio file
    S = librosa.feature.melspectrogram(y=signal, sr=rate, n_fft=2048, hop_length=512, n_mels=128)
    S_DB = librosa.power_to_db(S, ref=np.max)

    # Resize to (128, 128) if necessary
    if S_DB.shape != (128, 128):
        S_DB = librosa.util.fix_length(S_DB, size=40, axis=1)  # Adjust the width
        S_DB = librosa.util.fix_length(S_DB, size=40, axis=0)  # Adjust the height

    # Reshape to (128, 128, 3) for VGG19
    S_DB = np.expand_dims(S_DB, axis=-1)  # Add channel dimension (128, 128, 1)
    S_DB = np.repeat(S_DB, 3, axis=-1)    # Repeat grayscale to RGB (128, 128, 3)
    S_DB = np.expand_dims(S_DB, axis=0)  # Add batch dimension (1, 128, 128, 3)

    # Normalize
    S_DB = S_DB / 255.0  # Normalize to range [0, 1]

    # Predict genre
    prediction = model.predict(S_DB)
    predicted_label = np.argmax(prediction, axis=1)

    genres = ["blues", "classical", "country", "disco", "hiphop", "jazz", "metal", "pop", "reggae", "rock"]
    return genres[predicted_label[0]]

# Test prediction on a new file
file_path = "blues.00000.wav"  # Path to the test audio file
predicted_genre = predict_genre_vgg19(file_path, model)
print(f"The predicted genre is: {predicted_genre}")