TinyVox is a large-scale, cross-linguistic corpus of over half a million IPA-transcribed child vocalizations, curated from [PhonBank](https://talkbank.org/phon/). It covers five languages (English, French, Portuguese, German, and Spanish) and includes recordings from 560 children aged 6 months to 8 years across 31 source corpora. TinyVox standardizes heterogeneous phonetic annotations into a unified 57-phoneme inventory and provides ready-to-use train/validation/test splits designed for training and evaluating automatic phoneme recognition systems on child speech. It was introduced alongside [BabAR](https://github.com/MarvinLvn/BabAR), a phoneme recognition system for young children's speech.
 
---

## License and usage restrictions
 
TinyVox is derived from data hosted on [PhonBank](https://talkbank.org/phon/), part of the TalkBank system. It is therefore subject to TalkBank's [Ground Rules](https://talkbank.org/0share/rules.html) and distributed under **[CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/)**.
 
In practice, this means:
- TinyVox can be used for academic research, teaching, and non-commercial development.
- TinyVox **cannot** be used in commercial products or services. This includes training or fine-tuning models (e.g. LLMs, ASR systems) that will be deployed commercially.
- Any redistribution or adaptation of TinyVox must remain under the same license (ShareAlike) and retain attribution.

 
---

## Quickstart

TinyVox can be downloaded here: [https://talkbank.org/phon/access/Derived/TinyVox.html](https://talkbank.org/phon/access/Derived/TinyVox.html).

```
├── audio/
├── original/
├── metadata.csv
├── train.csv
├── val.csv
└── test.csv
```

| Folder / file | What it is                                                                                                                                                                                                                                             |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `audio/` | Child speech utterances (`.wav`), extracted from manually-annotated boundaries, listen to these to get a feel for the data                                                                                                                             |
| `original/` | Raw audio downloaded from TalkBank. **Not included** in the TinyVox `.zip` (179 GB), needed only if you want to retrain BabAR or use contextual information as in the paper. You can download it using `./download_original.sh` provided in this repo. |
| `metadata.csv` | Per-utterance metadata (see below)                                                                                                                                                                                                                     |
| `train.csv` / `val.csv` / `test.csv` | Same metadata, split the way we split it to train BabAR                                                                                                                                                                                                |
 
**`metadata.csv` columns:**
 
| Column | Description |
|---|---|
| `audio_filename` | Name of the `.wav` file in `audio/` |
| `original_audio_path` | Path to the source audio file, if you want to re-download it |
| `original_transcript_path` | Path to the source `.cha` transcript, if you want to re-download it |
| `language` | Language spoken by the child |
| `gender` | Gender of the child |
| `file_activity` | Type of recorded activity (e.g. toyplay, picture naming) |
| `age_months` | Child's age in months |
| `phones` | Manual phonetic transcription (after normalization) |
| `sentence` | Orthographic transcript, where available (not used in the paper) |
| `child_pseudoid` | Pseudo-anonymized child identifier, inferred from metadata |
| `onset` / `offset` | Utterance boundaries (ms) in the original file, for re-extraction |
 
See [REBUILDING.md](REBUILDING.md) for instructions on rebuilding TinyVox from scratch.

## References

```bibtex
@misc{babar,
      title={BabAR: from phoneme recognition to developmental measures of young children's speech production}, 
      author={Marvin Lavechin and Elika Bergelson and Roger Levy},
      year={2026},
      eprint={2603.05213},
      archivePrefix={arXiv},
      primaryClass={eess.AS},
      url={https://arxiv.org/abs/2603.05213}, 
}
```
