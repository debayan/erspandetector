import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import json
import sys

torch.manual_seed(1)

def prepare_sequence(seq, to_ix):
    idxs = [to_ix[w] for w in seq]
    return torch.tensor(idxs, dtype=torch.long)

#training_data = [
#    ("The dog ate the apple".split(), ["DET", "NN", "V", "DET", "NN"]),
#    ("Everybody read that book".split(), ["NN", "V", "DET", "NN"])
#]
#word_to_ix = {}
#for sent, tags in training_data:
#    for word in sent:
#        if word not in word_to_ix:
#            word_to_ix[word] = len(word_to_ix)
#print(word_to_ix)
#tag_to_ix = {"DET": 0, "NN": 1, "V": 2}


d = json.loads(open('wordvectorstraintest.json').read())
trainsplit = d[0:int(0.9*len(d))]
testsplit = d[int(0.9*len(d)):]
trainx = []
trainlabels = []
for item in trainsplit:
    trainx.append(item['wordvectors'])
    trainlabels.append(item['erspan'])

#trainxtensors = torch.tensor(trainx,dtype=torch.long)
#labelxtensors = torch.tensor(trainlabels,dtype=torch.int)

testx = []
testlabels = []
for item in testsplit:
    testx.append(item['wordvectors'])
    testlabels.append(item['erspan'])

#testxtensors = torch.tensor(testx,dtype=torch.long)
#testlabels = torch.tensor(testlabels,dtype=torch.int)


# These will usually be more like 32 or 64 dimensional.
# We will keep them small, so we can see how the weights change as we train.
EMBEDDING_DIM = 304
HIDDEN_DIM = 150


class LSTMTagger(nn.Module):
    def __init__(self, embedding_dim, hidden_dim, tagset_size):
        super(LSTMTagger, self).__init__()
        self.hidden_dim = hidden_dim


        # The LSTM takes word embeddings as inputs, and outputs hidden states
        # with dimensionality hidden_dim.
        self.lstm = nn.LSTM(embedding_dim, hidden_dim)

        # The linear layer that maps from hidden state space to tag space
        self.hidden2tag = nn.Linear(hidden_dim, tagset_size)

    def forward(self, sentence):
        lstm_out, _ = self.lstm(sentence)
        tag_space = self.hidden2tag(lstm_out)
        tag_scores = F.log_softmax(tag_space, dim=1)
        return tag_scores

model = LSTMTagger(EMBEDDING_DIM, HIDDEN_DIM, 3)
loss_function = nn.NLLLoss()
optimizer = optim.SGD(model.parameters(), lr=0.1)

# See what the scores are before training
# Note that element i,j of the output is the score for tag j for word i.
# Here we don't need to train, so the code is wrapped in torch.no_grad()
#with torch.no_grad():
#    inputs = prepare_sequence(training_data[0][0], word_to_ix)
#    tag_scores = model(inputs)
#    print(tag_scores)

for epoch in range(300):  # again, normally you would NOT do 300 epochs, it is toy data
    for x,label  in zip(trainx,trainlabels):
        try:
            # Step 1. Remember that Pytorch accumulates gradients.
            # We need to clear them out before each instance
            model.zero_grad()
    
            # Step 2. Get our inputs ready for the network, that is, turn them into
            # Tensors of word indices.
            tensorx = torch.tensor([x],dtype=torch.float)
            tensorlabel = torch.tensor([label],dtype=torch.long)
    
            # Step 3. Run our forward pass.
            tag_scores = model(tensorx)
            tag_scores = tag_scores.permute(0,2,1)
            #print(tag_scores,tag_scores.size())
            #print(tensorlabel,tensorlabel.size())
            # Step 4. Compute the loss, gradients, and update the parameters by
            #  calling optimizer.step()
            loss = loss_function(tag_scores, tensorlabel)
            print(loss)
            loss.backward()
            optimizer.step()
        except Exception:
            print("exc")

