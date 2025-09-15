import argparse, glob
from tokenizers import Tokenizer, trainers, models, pre_tokenizers, normalizers
from tokenizers.processors import BertProcessing

def main(args):
    files = sorted(glob.glob(f"{args.shards}/*.txt"))
    tok = Tokenizer(models.WordPiece(unk_token="[UNK]"))
    tok.normalizer = normalizers.Sequence([normalizers.NFKC()])
    tok.pre_tokenizer = pre_tokenizers.Whitespace()
    trainer = trainers.WordPieceTrainer(vocab_size=int(args.vocab_size),
                                        min_frequency=2,
                                        special_tokens=["[PAD]","[UNK]","[CLS]","[SEP]","[MASK]"])
    tok.train(files, trainer)
    outdir=args.out
    import os; os.makedirs(outdir, exist_ok=True)
    tok.save(f"{outdir}/tokenizer.json")
    with open(f"{outdir}/vocab.txt","w") as f:
        for tok_str,_ in tok.get_vocab().items():
            f.write(tok_str+"\n")
    print("Saved tokenizer to", outdir)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--shards", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--vocab-size", default="30000")
    p.add_argument("--cased", action="store_true")  # reserved
    main(p.parse_args())
