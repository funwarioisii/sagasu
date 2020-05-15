import tensorflow as tf


class BahdanauAttention(tf.keras.Model):
  def __init__(self, units):
    super(BahdanauAttention, self).__init__()
    self.W1 = tf.keras.layers.Dense(units)
    self.W2 = tf.keras.layers.Dense(units)
    self.V = tf.keras.layers.Dense(1)

  def call(self, features, hidden):
    hidden_with_time_axis = tf.expand_dims(hidden, 1)
    score = tf.nn.tanh(self.W1(features) + self.W2(hidden_with_time_axis))
    attention_weights = tf.nn.softmax(self.V(score), axis=1)
    context_vector = attention_weights * features
    context_vector = tf.reduce_sum(context_vector, axis=1)

    return context_vector, attention_weights


class CNNEncoder(tf.keras.Model):
  def __init__(self, embedding_dim):
    super(CNNEncoder, self).__init__()
    self.fc = tf.keras.layers.Dense(embedding_dim)

  def call(self, x):
    x = self.fc(x)
    x = tf.nn.relu(x)
    return x


class RNNDecoder(tf.keras.Model):
  def __init__(self, embedding_dim, units, vocab_size):
    super(RNNDecoder, self).__init__()
    self.units = units

    self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
    self.gru = tf.keras.layers.GRU(self.units,
                                   return_sequences=True,
                                   return_state=True,
                                   recurrent_initializer='glorot_uniform')
    self.fc1 = tf.keras.layers.Dense(self.units)
    self.fc2 = tf.keras.layers.Dense(vocab_size)

    self.attention = BahdanauAttention(self.units)

  def call(self, x, features, hidden):
    context_vector, attention_weights = self.attention(features, hidden)
    x = self.embedding(x)
    x = tf.concat([tf.expand_dims(context_vector, 1), x], axis=-1)
    output, state = self.gru(x)
    x = self.fc1(output)
    x = tf.reshape(x, (-1, x.shape[2]))
    x = self.fc2(x)
    return x, state, attention_weights

  def reset_state(self, batch_size):
    return tf.zeros((batch_size, self.units))


if __name__ == '__main__':
  images = tf.random.normal([1, 224, 224, 3])

  image_model = tf.keras.applications.MobileNetV2(
    include_top=False, weights='imagenet')
  new_input = image_model.input
  hidden_layer = image_model.layers[-1].output

  image_features_extract_model = tf.keras.Model(new_input, hidden_layer)
  features = image_features_extract_model(images)
  features = tf.reshape(features, (features.shape[0], -1, features.shape[3]))

  enc = CNNEncoder(embedding_dim=256)
  dec = RNNDecoder(embedding_dim=256, units=512, vocab_size=9880)

  dec.load_weights('../model/dec/dec_save_weights')

  enc.load_weights("../model/enc/enc_save_weights")
  encoded = enc(features)
  hidden = dec.reset_state(batch_size=1)
  print(encoded.shape)

  with open('../model/tokenize/token.json') as f:
    s = f.readline()
  tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(s)
  print((iw := tokenizer.index_word)[0], iw[1], iw[2], iw[3])

  result = []
  dec_input = tf.expand_dims([tokenizer.word_index['<start>']], 0)

  for i in range(100):
    print(result)
    print(dec_input.shape, features.shape, hidden.shape)
    predictions, hidden, attention_weights = dec(dec_input, encoded, hidden)

    predicted_id = tf.random.categorical(predictions, 1)[0][0].numpy()
    result.append(tokenizer.index_word[predicted_id])

    if tokenizer.index_word[predicted_id] == '<end>':
      break
    else:
      dec_input = tf.expand_dims([predicted_id], 0)
