#!/usr/bin/env python3
"""
Connection Finder — MiMo v2.5's research cross-referencer.
Finds hidden connections and shared themes across research topics.
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict
from itertools import combinations


RESEARCH_DIR = Path(__file__).parent / "research"
TOPICS = {
    "space": "Space & Astronomy",
    "science": "Mind-Bending Science",
    "world": "World Facts",
    "math": "Millennium Prize Problems",
    "paradoxes": "Real-World Paradoxes",
    "consciousness": "Hard Problem of Consciousness",
    "history": "Obscure History",
    "esolangs": "Esoteric Programming Languages",
    "p-zombies": "Philosophical Zombies",
    "other-minds": "Problem of Other Minds",
}

# Key concepts to track across topics
CONCEPTS = {
    "quantum": ["quantum", "superposition", "wave function", "measurement", "entanglement"],
    "consciousness": ["consciousness", "conscious", "awareness", "qualia", "subjective", "experience"],
    "time": ["time", "temporal", "arrow of time", "entropy", "chronological"],
    "limits": ["limit", "impossible", "intractable", "unsolvable", "barrier", "boundary"],
    "paradox": ["paradox", "contradiction", "puzzle", "mystery", "unsolved"],
    "evolution": ["evolution", "evolved", "natural selection", "adaptation", "species"],
    "information": ["information", "data", "computation", "algorithm", "complexity"],
    "infinity": ["infinite", "infinity", "unbounded", "endless", "limitless"],
    "measurement": ["measure", "measurement", "precision", "accuracy", "observation"],
    "emergence": ["emergence", "emergent", "arise", "gives rise", "fundamental"],
    "scale": ["scale", "size", "magnitude", "proportion", "scaling"],
    "collisions": ["collide", "collision", "contradict", "conflict", "tension"],
    "dark": ["dark", "invisible", "hidden", "unseen", "obscure"],
    "beauty": ["beauty", "elegant", "elegance", "beautiful", "art"],
    "parody": ["parody", "satire", "humor", "absurd", "absurdity"],
    "paradox_solutions": ["solution", "resolve", "resolution", "answer", "proof"],
}


def load_research():
    """Load all research files."""
    research = {}
    for filename in RESEARCH_DIR.glob("*.md"):
        key = filename.stem
        if key in TOPICS:
            content = filename.read_text(encoding="utf-8").lower()
            research[key] = {
                "title": TOPICS[key],
                "content": content,
                "words": set(re.findall(r'\b[a-z]+\b', content)),
            }
    return research


def find_shared_terms(research):
    """Find terms that appear across multiple topics."""
    term_topics = defaultdict(set)
    
    for key, data in research.items():
        for word in data["words"]:
            if len(word) > 4:  # Skip short words
                term_topics[word].add(key)
    
    # Find terms in 3+ topics
    shared = {}
    for term, topics in term_topics.items():
        if len(topics) >= 3:
            shared[term] = topics
    
    # Sort by number of topics
    return dict(sorted(shared.items(), key=lambda x: len(x[1]), reverse=True))


def find_concept_connections(research):
    """Find connections based on predefined concepts."""
    connections = []
    
    for concept_name, keywords in CONCEPTS.items():
        topic_concept = {}
        for key, data in research.items():
            count = sum(data["content"].count(kw) for kw in keywords)
            if count > 0:
                topic_concept[key] = count
        
        if len(topic_concept) >= 2:
            # Find strongest connections
            topics = list(topic_concept.keys())
            for t1, t2 in combinations(topics, 2):
                connections.append({
                    "concept": concept_name,
                    "topic1": TOPICS[t1],
                    "topic2": TOPICS[t2],
                    "strength1": topic_concept[t1],
                    "strength2": topic_concept[t2],
                    "total": topic_concept[t1] + topic_concept[t2],
                })
    
    # Sort by total strength
    connections.sort(key=lambda x: x["total"], reverse=True)
    return connections


def find_thematic_overlaps(research):
    """Find thematic overlaps between topic pairs."""
    overlaps = []
    
    for (k1, d1), (k2, d2) in combinations(research.items(), 2):
        # Jaccard similarity on significant words
        significant1 = {w for w in d1["words"] if len(w) > 5}
        significant2 = {w for w in d2["words"] if len(w) > 5}
        
        intersection = significant1 & significant2
        union = significant1 | significant2
        
        if union:
            similarity = len(intersection) / len(union)
            if similarity > 0.05:  # Threshold
                overlaps.append({
                    "topic1": d1["title"],
                    "topic2": d2["title"],
                    "similarity": similarity,
                    "shared_words": sorted(intersection)[:15],
                })
    
    overlaps.sort(key=lambda x: x["similarity"], reverse=True)
    return overlaps


def print_report(research):
    """Print full connection report."""
    print("=" * 60)
    print("  Connection Finder — MiMo v2.5")
    print("  Cross-referencing research topics")
    print("=" * 60)
    
    # 1. Shared terms
    print("\n[1] SHARED TERMS (appearing in 3+ topics)")
    print("-" * 60)
    shared = find_shared_terms(research)
    for term, topics in list(shared.items())[:20]:
        topic_names = [TOPICS[t] for t in sorted(topics)]
        print(f"  {term}: {' <-> '.join(topic_names)}")
    
    # 2. Concept connections
    print("\n[2] CONCEPT CONNECTIONS")
    print("-" * 60)
    connections = find_concept_connections(research)
    seen = set()
    for conn in connections[:15]:
        key = (conn["concept"], conn["topic1"], conn["topic2"])
        if key not in seen:
            seen.add(key)
            print(f"  {conn['concept'].upper()}")
            print(f"    {conn['topic1']} (x{conn['strength1']}) <-> {conn['topic2']} (x{conn['strength2']})")
    
    # 3. Thematic overlaps
    print("\n[3] THEMATIC OVERLAPS (strongest similarity)")
    print("-" * 60)
    overlaps = find_thematic_overlaps(research)
    for overlap in overlaps[:10]:
        print(f"  {overlap['topic1']} <-> {overlap['topic2']}")
        print(f"    Similarity: {overlap['similarity']:.1%}")
        print(f"    Shared: {', '.join(overlap['shared_words'][:8])}")
        print()
    
    # 4. The big picture
    print("\n[4] THE BIG PICTURE")
    print("-" * 60)
    print("  Patterns across all research:")
    print()
    
    # Find dominant themes
    all_concepts = defaultdict(int)
    for conn in connections:
        all_concepts[conn["concept"]] += conn["total"]
    
    for concept, score in sorted(all_concepts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  • {concept.upper()} — appears across multiple topics with total weight {score}")
    
    print()
    print("  The research reveals interconnected themes:")
    print("  - Limits and boundaries appear everywhere (math, physics, language, consciousness)")
    print("  - Quantum mechanics connects to consciousness, time, and information")
    print("  - Paradoxes often arise from colliding frameworks")
    print("  - Evolution and emergence show up across biology, computing, and physics")
    print("  - The boundary between possible and impossible is thinner than expected")


if __name__ == "__main__":
    if not RESEARCH_DIR.exists():
        print(f"Research directory not found: {RESEARCH_DIR}")
        sys.exit(1)
    
    research = load_research()
    if not research:
        print("No research files found.")
        sys.exit(1)
    
    print_report(research)
