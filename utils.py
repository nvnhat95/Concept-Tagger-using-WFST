import os, math, glob
from collections import defaultdict
import wrapper


def create_word_concept_dataset(working_dir):
    with open("./datasets/NL2SparQL4NLU.train.conll.txt") as f:
        content = f.read().strip('\n').split('\n\n')

    with open(os.path.join(working_dir, 'train_data.txt'), 'w') as fout:
        for sentence in content:
            list_word_tag =  [(x.split('\t')[0], x.split('\t')[1]) for x in sentence.split('\n')]
            
            for i in range(len(list_word_tag)):
                tag = list_word_tag[i][1]
                if tag == 'O':
                    tag = 'O-' + list_word_tag[i][0]
                fout.write("{}\t{}\n".format(list_word_tag[i][0], tag))
            fout.write('\n')


def load_training_data(working_dir, train_data_path):
    """
    Load and return training data which is a list containing pairs (word, tag)
    Simultaneously extract tags and write to 'tags.txt' in working directory
    """
    training_data = []

    with open(train_data_path) as f:
        content = f.read().strip('\n').split('\n\n')
    
    with open(os.path.join(working_dir, 'tags.txt'), 'w') as fout:
        for sentence in content:
            list_word_tag =  [(x.split('\t')[0], x.split('\t')[1]) for x in sentence.split('\n')]
            
            training_data += list_word_tag

            list_tags = [x[1] for x in list_word_tag]
            fout.write(' '.join(list_tags) +  '\n')

    return training_data


def create_lexicon_file(working_dir, train_data_path):
    """
    Create lexicon and write to 'lex.txt' in working directory
    """
    os.system("ngramsymbols < {} > {}/lex.txt".format(train_data_path, working_dir))


def create_wfst(training_data, working_dir):
    """
    Create fst defination and write to 'graph.txt' in working directory
    """
    # counting
    tag_count = defaultdict(int)
    word_tag_count = defaultdict(int)
    for t in training_data:
        tag_count[t[1]] += 1
        word_tag = "{}#{}".format(t[0], t[1])
        word_tag_count[word_tag] += 1

    # caculating p(w|tag) = count(w, tag) / count(tag):
    p_word_tag = defaultdict(float)
    for word_tag in word_tag_count:
        _, tag = word_tag.split('#')
        p_word_tag[word_tag] = - math.log(word_tag_count[word_tag] / tag_count[tag])
    for tag in tag_count:
        p_word_tag["<unk>#{}".format(tag)] = - math.log(1 / (len(tag_count)))


    # write graph defination to file
    with open(os.path.join(working_dir, 'graph.txt'), 'w') as f:
        for word_tag in p_word_tag:
            word, tag = word_tag.split('#')
            f.write("0\t0\t{}\t{}\t{}\n".format(word, tag, p_word_tag[word_tag]))
        f.write('0')

    wrapper.compile_transducer('graph.txt', 'lex.txt', directory=working_dir)


def compile_language_model(training_data, working_dir, ngram=2, smoothing='witten_bell', output_file=None):
    """"
    compile language model and write to output_file in working directory/language_models 
    """
    if not os.path.isdir(os.path.join(working_dir, 'language_models')):
        os.mkdir(os.path.join(working_dir, 'language_models'))

    if output_file is None:
        output_file = "{}-{}.lm".format(smoothing, ngram)
    os.system("cd {} \
              && farcompilestrings --symbols=lex.txt --unknown_symbol='<unk>' tags.txt > tags.far \
              && ngramcount --order={}  --require_symbols=false tags.far > tags.cnts \
              && ngrammake --method={} tags.cnts > language_models/{}".format(working_dir, ngram, smoothing, output_file))


def predict_on_testset(transducer_file, text_file_path, langugage_model_file=None, 
                       groundtruth_file=None, output_file='result/prediction.txt', working_dir='./'):
    """
    Predict on test ste and write result to output file
    """
    os.system("cp {} {}/test.txt".format(text_file_path, working_dir))
    
    wrapper.compile_text_file_to_fsm('fst', 'test.txt', 'lex.txt', working_dir)
    
    if groundtruth_file is not None:
        with open(groundtruth_file) as f:
            groundtruth = f.read().strip('\n').split('\n\n')
        
    with open(os.path.join(working_dir, output_file), 'w') as fout:

        for i, fst_test in enumerate(sorted(glob.glob("{}/test*.fst".format(working_dir)))):
            fst_test_filename = os.path.basename(fst_test)

            wrapper.compose_fsts(fst_test_filename, transducer_file, 'composed.fst', working_dir)
            if langugage_model_file is not None:
                wrapper.compose_fsts('composed.fst', langugage_model_file, 'composed_tag.fst', working_dir)
                os.system("cd {} && mv composed_tag.fst composed.fst \
                            && fstrmepsilon composed.fst composed.fst".format(working_dir))

            wrapper.get_shortest_path('composed.fst', 'shortest_path.fst', working_dir)
            wrapper.sort_fst('shortest_path.fst', 'shortest_path.fst', working_dir)

            response = wrapper.get_fstprint('fst', 'lex.txt', 'shortest_path.fst', working_dir)
            res = []
            for line in response.split('\n'):
                t = line.split('\t')
                if len(t) > 3:
                    res.append((t[2], t[3]))

            if groundtruth_file is None:
                for t in res:
                    fout.write("{} {}\n".format(t[0], t[1]))
            else:
                for t in zip(groundtruth[i].split('\n'), res):
                    fout.write("{} {}\n".format(t[0].replace('\t', ' '), t[1][1]))
            fout.write('\n')


def evaluate(prediction_file, result_dir):
    output_file = "score_{}".format(prediction_file)
    os.system("perl conlleval.pl <{}> {}".format(os.path.join(result_dir, prediction_file), os.path.join(result_dir, output_file)))
    return output_file

def find_best_config(training_data, working_dir, \
                        ngrams=[2, 3, 4, 5], \
                        smooth_methods = ["absolute", "katz", "kneser_ney", "presmoothed", "unsmoothed", "witten_bell"]):

    result_dir = os.path.join(working_dir, 'result')
    if not os.path.isdir(result_dir):
        os.mkdir(result_dir)

    for ngram in ngrams:
        print("Ngram: ", ngram)
        for method in smooth_methods:
            print("\tMethod {} :\t".format(method), end='')
            if os.path.isfile(os.path.join(working_dir, 'result/score_pred_{}-{}.txt'.format(method, ngram))):
                print("done")
                continue

            # create language model
            langugage_model_file = os.path.join('language_models', "{}-{}.lm".format(method, ngram))
            compile_language_model(training_data, working_dir=working_dir, ngram=ngram, smoothing=method)

            # predict and write to file
            output_file = "pred_{}-{}.txt".format(method, ngram)
            predict_on_testset('graph.fst', os.path.join(working_dir, 'test_utterences.txt'), langugage_model_file=langugage_model_file, \
                       groundtruth_file=os.path.join(working_dir, 'test_references.txt'), output_file="result/{}".format(output_file), \
                        working_dir=working_dir)
            score_file = evaluate(output_file, result_dir)

            with open(os.path.join(result_dir, score_file)) as f:
                f.readline()                
                print("F1 score {}".format(f.readline()[-6:]))
    print("Done!")

    # remove temp files
    os.system("cd {} && rm test*.fst shortest_path.fst composed*.fst".format(working_dir))
