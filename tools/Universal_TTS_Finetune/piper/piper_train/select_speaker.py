#!/usr/bin/env python3
import argparse
import csv
import sys
from collections import Counter, defaultdict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--speaker-number", type=int)
    parser.add_argument("--speaker-name")
    args = parser.parse_args()

    assert (args.speaker_number is not None) or (args.speaker_name is not None)

    reader = csv.reader(sys.stdin, delimiter="|")
    writer = csv.writer(sys.stdout, delimiter="|")

    if args.speaker_name is not None:
        for row in reader:
            audio, speaker_id, text = row[0], row[1], row[-1]
            if args.speaker_name == speaker_id:
                writer.writerow((audio, text))
    else:
        utterances = defaultdict(list)
        counts = Counter()
        for row in reader:
            audio, speaker_id, text = row[0], row[1], row[-1]
            utterances[speaker_id].append((audio, text))
            counts[speaker_id] += 1

        writer = csv.writer(sys.stdout, delimiter="|")
        for i, (speaker_id, _count) in enumerate(counts.most_common()):
            if i == args.speaker_number:
                for row in utterances[speaker_id]:
                    writer.writerow(row)

                print(speaker_id, file=sys.stderr)
                break


if __name__ == "__main__":
    main()
