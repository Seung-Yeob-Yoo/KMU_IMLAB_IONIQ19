import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.layers import Masking, Dense, Concatenate, LSTM
from tensorflow.keras.initializers import Constant

class BiasLayer(tf.keras.layers.Layer):
    def __init__(self, *args, **kwargs):
        super(BiasLayer, self).__init__(*args, **kwargs)

    def build(self, input_shape):
        self.bias = self.add_weight('bias',
                                    shape=(1,),
                                    initializer='zeros',
                                    trainable=True)
    def call(self, x):
        return x + self.bias

class DeepONet(Model):
    def __init__(self, num_branchs, num_layers, num_nodes, num_out, activation, norm_factors, RNN=False, P1_init=None, P2_init=None):
        super().__init__()
        # self.masking = Masking(mask_value=0.)
        self.num_branchs = num_branchs
        if self.num_branchs > 2:
            raise NotImplementedError
        
        self.RNN = RNN
        if self.RNN:
            self.masking = Masking(mask_value=0.)
            self.branch_in = LSTM(num_nodes)
        self.num_out = num_out
        self.num_layers = num_layers
        self.branchs = [[Dense(num_nodes, activation=activation, name=f'branch_{i}') for i in range(num_layers)] for _ in range(self.num_branchs)]
        self.branch_outs = [[Dense(num_nodes, activation=activation, name=f'branch_out_{i}') for i in range(num_out)] for _ in range(self.num_branchs)]
        self.trunks = [Dense(num_nodes, activation=activation, name=f'trunk_{i}') for i in range(num_layers)]
        self.bias = [BiasLayer(name=f'bias_{i}') for i in range(num_out)]
        self.concat = Concatenate()
        
        self.norm_factors = norm_factors
        
        if P1_init is not None:
            self.P1_gain = self.add_weight(name='P1',
                                        shape=(1,),
                                        initializer=Constant(value=P1_init),
                                        trainable=True)
        if P2_init is not None:
            self.P2_gain = self.add_weight(name='P2',
                                        shape=(1,),
                                        initializer=Constant(value=P2_init),
                                        trainable=True)
    
    def call(self, branch_in, trunk_in):
        branch_zs = []
        
        for i in range(self.num_branchs):
            branch_zs.append(branch_in[i] / self.norm_factors[i])
            if self.RNN:
                branch_zs[i] = self.masking(branch_zs[i])
                branch_zs[i] = self.branch_in(branch_zs[i])
            for branch_layer in self.branchs[i]:
                branch_zs[i] = branch_layer(branch_zs[i])
                
        trunk_z = trunk_in / self.norm_factors[-1]
        for trunk_layer in self.trunks:
            trunk_z = trunk_layer(trunk_z)
        
        branch_outputs = []
        for i in range(self.num_branchs):
            for b in range(self.num_out):
                branch_outputs.append(self.branch_outs[i][b](branch_zs[i]))
        
        outputs = []
        for b in range(self.num_out):
            if self.num_branchs > 1:
                dot_product = tf.multiply(branch_outputs[b], branch_outputs[b+self.num_branchs])
            else:
                dot_product = branch_outputs[b]
            dot_product = tf.multiply(dot_product, trunk_z)
            outputs.append(self.bias[b](tf.reduce_sum(dot_product, axis=1, keepdims=True)))
            
        output = self.concat(outputs)
        
        return output

def get_DeepONet_Roll(num_nodes, activation):
    input_b = tf.keras.Input(shape=(500,))
    input_t = tf.keras.Input(shape=(1,))
    
    hidden_b = input_b / 9.80665
    
    hidden_b = Dense(num_nodes, activation=activation, name='branch_0')(hidden_b)
    hidden_b = Dense(num_nodes, activation=activation, name='branch_1')(hidden_b)
    hidden_b = Dense(num_nodes, activation=activation, name='branch_2')(hidden_b)
    hidden_b = Dense(num_nodes, activation=activation, name='branch_3')(hidden_b)
    hidden_b = Dense(num_nodes, activation=activation, name='branch_4')(hidden_b)
    hidden_b = Dense(num_nodes, activation=activation, name='branch_5')(hidden_b)
    
    output_b_1 = Dense(num_nodes, activation=activation, name='branch_out_0')(hidden_b)
    output_b_2 = Dense(num_nodes, activation=activation, name='branch_out_1')(hidden_b)
    
    hidden_t = input_t / 5.0
    
    hidden_t = Dense(num_nodes, activation=activation, name='trunk_0')(hidden_t)
    hidden_t = Dense(num_nodes, activation=activation, name='trunk_1')(hidden_t)
    hidden_t = Dense(num_nodes, activation=activation, name='trunk_2')(hidden_t)
    hidden_t = Dense(num_nodes, activation=activation, name='trunk_3')(hidden_t)
    hidden_t = Dense(num_nodes, activation=activation, name='trunk_4')(hidden_t)
    hidden_t = Dense(num_nodes, activation=activation, name='trunk_5')(hidden_t)
    
    dot_product_1 = tf.keras.layers.Dot(axes=1)([output_b_1, hidden_t])
    dot_product_2 = tf.keras.layers.Dot(axes=1)([output_b_2, hidden_t])
    
    output_1 = BiasLayer(name='bias_0')(dot_product_1)
    output_2 = BiasLayer(name='bias_1')(dot_product_2)
    
    output = Concatenate()([output_1, output_2])
    
    model = tf.keras.Model(inputs=[input_b, input_t], outputs=output)
    
    return model

import os
import yaml
from glob import glob
import numpy as np
def get_origin_model(model_path):
    isTL = True if os.path.basename(model_path)[-2:] == 'TL' else False
    
    config_path = os.path.join(model_path, 'config.yaml')
    with open(config_path) as f:
        config_dic = yaml.load(f, Loader=yaml.FullLoader)
    
    model = get_DeepONet_Roll(
        num_nodes=config_dic['num_nodes'],
        activation=config_dic['activation'],
    )
    if isTL:
        model.P1_gain = model.add_weight(name='P1',
                        shape=(1,),
                        initializer=tf.keras.initializers.Constant(value=1.0),
                        trainable=True)
        model.P2_gain = model.add_weight(name='P2',
                        shape=(1,),
                        initializer=tf.keras.initializers.Constant(value=1.0),
                        trainable=True)
    model.summary()
    
    model_base = DeepONet(
        num_branchs = config_dic['num_branchs'],
        num_out = 2,
        num_layers=config_dic['num_layers'],
        num_nodes=config_dic['num_nodes'],
        activation=config_dic['activation'],
        norm_factors=config_dic['norm_factors'],
        RNN=True if config_dic['model'] == 'RNN' else False,
        P1_init=config_dic['P1_init'],
        P2_init=config_dic['P2_init'],
    )
    best_weights_path = glob(os.path.join(model_path, 'best_*.h5'))[0]
    
    # input dummy input for similarity build
    dummy_u = np.random.rand(model_base.num_branchs, 1, 500).astype(np.float32)
    dummy_t = np.random.rand(1, 1).astype(np.float32)
    # print(dummy_u.shape, dummy_t.shape)
    model_base(dummy_u, dummy_t)
    # model_base.summary()
    # model.summary()
        
    model_base.load_weights(best_weights_path)
    layer_names = [
        'branch_0',
        'branch_1',
        'branch_2',
        'branch_3',
        'branch_4',
        'branch_5',
        'branch_out_0',
        'branch_out_1',
        'trunk_0',
        'trunk_1',
        'trunk_2',
        'trunk_3',
        'trunk_4',
        'trunk_5',
        'bias_0',
        'bias_1',
    ]
    
    for layer_name in layer_names:
        # print(model.get_layer(layer_name).get_weights())
        model.get_layer(layer_name).set_weights(model_base.get_layer(layer_name).get_weights())
        # print(model.get_layer(layer_name).get_weights())
    
    if isTL:
        model.P1_gain.assign(model_base.P1_gain.numpy())
        model.P2_gain.assign(model_base.P2_gain.numpy())
        
    return model