import baseline
import variations
import utils
import os, argparse

def get_args():
    parser = argparse.ArgumentParser(description='movie concept tagger')

    parser.add_argument('--version', default='baseline', type=str, help="version of model: {'baseline', 'variation1', 'variation2', 'variation3'}")
    parser.add_argument('--mode', default='benchmark', type=str, help="{'bench_mark', 'single'} run the benchmark benchmark between configurations or a single configuration")
    parser.add_argument('--method', default='absolute-2', type=str, help="in case run single config, specify the smoothing method with format <method_name>-<gram>. e.g: 'absolute-2'. Available methods: {'absolute', 'katz', 'kneser_ney', 'presmoothed', 'unsmoothed', 'witten_bell'}")
    parser.add_argument('--iscontinue', default=True, type=bool, \
                         help='continue running the benchmark between configurations (ignore finished ones) or erase all and run from scratch')

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = get_args()

    ngrams=[2, 3, 4, 5]
    smooth_methods = ["absolute", "katz", "kneser_ney", "presmoothed", "unsmoothed", "witten_bell"]
    if args.mode == 'single':
        smooth_methods = [args.method.split('-')[0]]
        ngrams = [args.method.split('-')[1]]
    
    versions = {'baseline': variations.baseline(), \
                'variation1': variations.variation1(), \
                'variation2': variations.variation2(), \
                'variation3': variations.variation3()}
    model = versions[args.version]

    if not args.iscontinue:
        try:
            os.system("rm -r {}".format(working_dir))
        except:
            pass

    if not os.path.isdir(model.working_dir):
        os.mkdir(model.working_dir)

    model.create_train_data()
    model.create_test_data()

    train_data_path = os.path.join(model.working_dir, 'train_data.txt')
    training_data = utils.load_training_data(model.working_dir, train_data_path)

    # create lexicon
    utils.create_lexicon_file(model.working_dir, train_data_path)

    # create wfst
    utils.create_wfst(training_data, model.working_dir)

    # run the evaluation with different configurations
    utils.find_best_config(training_data, model.working_dir, ngrams=ngrams, smooth_methods=smooth_methods)
