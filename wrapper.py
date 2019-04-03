import os
import subprocess

def transform_sentence_for_wfst(sentence, out_file_path):
    s = ""
    for word in sentence.split(' ')[:-1]:
        s += word + ' <s> '
    s += sentence.split(' ')[-1]
    with open(out_file_path, 'w') as f:
        f.write(s.strip('\n'))
        

def compile_text_file_to_fsm(fsm_type, text_file, lex_file, directory='./'):
    assert fsm_type in {'fsa', 'fst'}
    
    os.system("cd {} && cat {} | \
                farcompilestrings --symbols={} --unknown_symbol='<unk>' --generate_keys=4 | \
                farextract --filename_prefix={} --filename_suffix='.{}'"\
             .format(directory, text_file, lex_file, text_file.split('.')[0], fsm_type))
    
    
def compile_transducer(transducer_defination_file, lex_file, out_file=None, directory='./'):
    if out_file is None:
        out_file = transducer_defination_file.split('.')[0] + '.fst'
        
#     os.system("cd {} && fstcompile --isymbols={} --osymbols={} {} > {}"\
#              .format(directory, lex_file, lex_file, transducer_defination_file, out_file))
    
    output = subprocess.check_output("cd {} && fstcompile --isymbols={} --osymbols={} {} > {}"\
                                     .format(directory, lex_file, lex_file, transducer_defination_file, out_file), shell=True)
    return "{}\nOutput file: {}".format(output.decode('utf-8'), out_file)


def compose_fsts(fst1_file, fst2_file, out_file=None, directory='./'):
    if out_file is None:
        out_file = "{}_{}.fst".format(fst1_file.split('.')[0], fst2_file.split('.')[0])
    
#     os.system("cd {} && fstcompose {} {} > {}"\
#              .format(directory, fst1_file, fst2_file, out_file))
    
    output = subprocess.check_output("cd {} && fstcompose {} {} > {}"\
             .format(directory, fst1_file, fst2_file, out_file), shell=True)
    
    return "{}\nOutput file: {}".format(output.decode('utf-8'), out_file)


def get_fstprint(fsm_type, lex_file, fsm_file, directory='./'):
    assert fsm_type in {'fsa', 'fst'}
    
    if fsm_type == 'fsa':
        output = subprocess.check_output("cd {} && fstprint --acceptor --isymbols={} {}"\
                                         .format(directory, lex_file, fsm_file), shell=True)
    else:
        output = subprocess.check_output("cd {} && fstprint --isymbols={} --osymbols={} {}"\
                                         .format(directory, lex_file, lex_file, fsm_file), shell=True)
    
    return output.decode('utf-8')


def draw_fsm(fsm_type, lex_file, fsm_file, out_img_file=None, directory='./'):
    assert fsm_type in {'fsa', 'fst'}
    
    if out_img_file is None:
        out_img_file = fsm_file.split('.')[0] + '.png'
    if fsm_type == 'fst':
        os.system("cd {} && fstdraw --isymbols={} --osymbols={} {} | dot -Tpng > {}"\
                 .format(directory, lex_file, lex_file, fsm_file, out_img_file))
    elif fsm_type == 'fsa':
        os.system("cd {} && fstdraw --acceptor --isymbols={} {} |dot -Tpng > {}"\
                 .format(directory, lex_file, fsm_file, out_img_file))
        
        
def get_shortest_path(fst_file, out_file = 'shortest_path.fst', directory='./'):
    os.system("cd {} && fstshortestpath {} shortest_path.fst".format(directory, fst_file))
    

def sort_fst(fst_file, out_file, working_dir='./'):
    os.system("cd {} && fsttopsort {} {}".format(working_dir, fst_file, out_file))
