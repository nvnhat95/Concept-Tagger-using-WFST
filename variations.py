import os
import utils

class baseline(object):
    def __init__(self):
        self.working_dir = "./baseline"

    def create_train_data(self):
        os.system("cp ./datasets/NL2SparQL4NLU.train.conll.txt {}/train_data.txt".format(self.working_dir))

    def create_test_data(self):
        os.system("cp ./datasets/NL2SparQL4NLU.test.utterances.txt {}/test_utterences.txt".format(self.working_dir))
        os.system("cp ./datasets/NL2SparQL4NLU.test.conll.txt {}/test_references.txt".format(self.working_dir))


class variation1(baseline):
    def __init__(self):
        self.working_dir = "./variation1"

    def create_train_data(self):
        with open("./datasets/NL2SparQL4NLU.train.conll.txt") as f:
            content1 = f.read().strip('\n').split('\n\n')

        with open("./datasets/NL2SparQL4NLU.train.features.conll.txt") as f:
            content2 = f.read().strip('\n').split('\n\n')

        with open(os.path.join(self.working_dir, 'train_data.txt'), 'w') as fout:
            for sentence1, sentence2 in zip(content1, content2):
                list_tags =  [x.split('\t')[1] for x in sentence1.split('\n')]
                list_lemmas =  [x.split('\t')[2] for x in sentence2.split('\n')]
                
                for lemma, tag in zip(list_lemmas, list_tags):
                    fout.write("{}\t{}\n".format(lemma, tag))
                fout.write('\n')

    def create_test_data(self):
        with open("./datasets/NL2SparQL4NLU.test.conll.txt") as f:
            content1 = f.read().strip('\n').split('\n\n')

        with open("./datasets/NL2SparQL4NLU.test.features.conll.txt") as f:
            content2 = f.read().strip('\n').split('\n\n')

        with open(os.path.join(self.working_dir, 'test_references.txt'), 'w') as fout1:
            with open(os.path.join(self.working_dir, 'test_utterences.txt'), 'w') as fout2:
                for sentence1, sentence2 in zip(content1, content2):
                    list_tags =  [x.split('\t')[1] for x in sentence1.split('\n')]
                    list_lemmas =  [x.split('\t')[2] for x in sentence2.split('\n')]
                
                    for lemma, tag in zip(list_lemmas, list_tags):
                        fout1.write("{}\t{}\n".format(lemma, tag))
                    fout1.write('\n')
                    fout2.write(" ".join(list_lemmas) + '\n')


class variation2(baseline):
    def __init__(self):
        self.working_dir = "./variation2"

    def create_train_data(self):
        with open("./datasets/NL2SparQL4NLU.train.conll.txt") as f:
            content = f.read().strip('\n').split('\n\n')

        with open(os.path.join(self.working_dir, 'train_data.txt'), 'w') as fout:
            for sentence in content:
                list_word_tag =  [(x.split('\t')[0], x.split('\t')[1]) for x in sentence.split('\n')]
                
                for i in range(len(list_word_tag)):
                    tag = list_word_tag[i][1]
                    if tag == 'O':
                        tag = 'O-' + list_word_tag[i][0]
                    fout.write("{}\t{}\n".format(list_word_tag[i][0], tag))
                fout.write('\n')

    def create_test_data(self):
        super().create_test_data()


class variation3(baseline):
    def __init__(self):
        self.working_dir = "./variation3"

    def create_train_data(self):
        with open("./datasets/NL2SparQL4NLU.train.conll.txt") as f:
            content = f.read().strip('\n').split('\n\n')

        with open(os.path.join(self.working_dir, 'train_data.txt'), 'w') as fout:
            for sentence in content:
                list_word_tag =  [(x.split('\t')[0], x.split('\t')[1]) for x in sentence.split('\n')]
                
                for i in range(len(list_word_tag)):
                    phrase, tag = list_word_tag[i]
                    if tag == 'O':
                        tag = 'O-' + list_word_tag[i][0]
                    if 'actor.name' in tag or 'character.name' in tag or 'person.name' in tag or 'director.name' in tag:
                        phrase = 'person.name'
                    if 'movie.location' in tag or 'country.name' in tag:
                        phrase = 'country.name'
                    fout.write("{}\t{}\n".format(phrase, tag))
                fout.write('\n')


    def create_test_data(self):
        with open("./datasets/NL2SparQL4NLU.test.conll.txt") as f:
            content = f.read().strip('\n').split('\n\n')

        with open(os.path.join(self.working_dir, 'test_references.txt'), 'w') as fout1:
            with open(os.path.join(self.working_dir, 'test_utterences.txt'), 'w') as fout2:
                for sentence in content:
                    list_word_tag =  [(x.split('\t')[0], x.split('\t')[1]) for x in sentence.split('\n')]
                    phrases = []
                    for i in range(len(list_word_tag)):
                        phrase, tag = list_word_tag[i]
                        if tag == 'O':
                            tag = 'O-' + list_word_tag[i][0]
                        if 'actor.name' in tag or 'character.name' in tag or 'person.name' in tag or 'director.name' in tag:
                            phrase = 'person.name'
                        if 'movie.location' in tag or 'country.name' in tag:
                            phrase = 'country.name'
                        phrases.append(phrase)
                        fout1.write("{}\t{}\n".format(phrase, tag))
                    fout1.write('\n')
                    fout2.write(' '.join(phrases) + '\n')

