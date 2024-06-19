# -*- coding: utf-8 -*-
"""model2_training_script.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1boBO59MZEL04P0eMtITnh9ushBwAQQUZ
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

# Function to preprocess data
def preprocess_data(file_path):
    xls = pd.ExcelFile(file_path)
    products = pd.read_excel(xls, sheet_name='product')

    # Handle missing values
    products['product_name'] = products['product_name'].fillna('')
    products['category'] = products['category'].fillna('')
    products['color'] = products['color'].fillna('')
    products['size'] = products['size'].fillna('')
    products['rent_price'] = products['rent_price'].fillna(0).astype(float)
    products['count_num_rating'] = products['count_num_rating'].fillna(0).astype(int)
    products['avg_rating'] = products['avg_rating'].fillna(0).astype(float)

    # Combine text and numerical features into a single feature
    products['features'] = (products['product_name'] + ' ' +
                            products['category'] + ' ' +
                            products['color'] + ' ' +
                            products['size'] + ' ' +
                            products['rent_price'].astype(str) + ' ' +
                            products['count_num_rating'].astype(str) + ' ' +
                            products['avg_rating'].astype(str))

    return products

# Function to preprocess data, vectorize, scale, combine, and calculate similarity
def vectorize_scale_combine_calculate(products):
    # Vectorize text features
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(products['features'])

    # Scale numerical features
    scaler = StandardScaler()
    numerical_features = scaler.fit_transform(products[['rent_price', 'count_num_rating', 'avg_rating']])

    # Combine TF-IDF matrix and scaled numerical features
    features_matrix = np.hstack((tfidf_matrix.toarray(), numerical_features))

    # Calculate similarity scores (cosine similarity)
    similarity_matrix = cosine_similarity(features_matrix, features_matrix)

    return features_matrix, similarity_matrix

# Function to create and train model
def create_and_train_model(features_matrix, labels, num_epochs=100, batch_size=64, model_save_path='model2.h5'):
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(256, activation='relu', input_shape=(features_matrix.shape[1],)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(len(labels), activation='softmax')
    ])

    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Train the model
    history = model.fit(features_matrix, labels, epochs=num_epochs, batch_size=batch_size)

    # Save the model
    model.save(model_save_path)
    print(f"Model saved to {model_save_path}")

    return model

# Function to execute the entire process
def main(file_path):
    # Preprocess data
    products = preprocess_data(file_path)

    # Vectorize, scale, combine, and calculate similarity
    features_matrix, similarity_matrix = vectorize_scale_combine_calculate(products)

    # Train and save the model
    labels = products.index  # Assuming index as labels for simplicity
    trained_model = create_and_train_model(features_matrix, labels, model_save_path='model2.h5')

    # Evaluate model on training data
    loss, accuracy = trained_model.evaluate(features_matrix, labels)
    print("Final Loss:", loss)
    print("Final Accuracy:", accuracy)

if __name__ == "__main__":
    file_path = '/content/data_for_model2.xlsx'  # feel free to change it
    main(file_path)
