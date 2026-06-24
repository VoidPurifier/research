#!/usr/bin/env python3
"""
Research Browser — MiMo v2.5's research collection viewer.
Browse, search, and explore the research files interactively.
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict


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
}


def load_research():
    """Load all research files and return structured data."""
    research = {}
    for filename in RESEARCH_DIR.glob("*.md"):
        key = filename.stem
        if key in TOPICS:
            content = filename.read_text(encoding="utf-8")
            sections = parse_sections(content)
            research[key] = {
                "title": TOPICS[key],
                "content": content,
                "sections": sections,
                "word_count": len(content.split()),
                "section_count": len(sections),
            }
    return research


def parse_sections(content):
    """Parse markdown content into sections."""
    sections = []
    current = None
    for line in content.split("\n"):
        if line.startswith("## "):
            if current:
                sections.append(current)
            current = {"title": line[3:].strip(), "content": ""}
        elif current:
            current["content"] += line + "\n"
    if current:
        sections.append(current)
    return sections


def search_research(research, query):
    """Search across all research for a query."""
    results = []
    query_lower = query.lower()
    for key, data in research.items():
        for section in data["sections"]:
            if query_lower in section["content"].lower() or query_lower in section["title"].lower():
                # Get the matching line with context
                for line in section["content"].split("\n"):
                    if query_lower in line.lower():
                        results.append({
                            "topic": data["title"],
                            "section": section["title"],
                            "line": line.strip(),
                        })
                        break
    return results


def print_stats(research):
    """Print collection statistics."""
    total_words = sum(d["word_count"] for d in research.values())
    total_sections = sum(d["section_count"] for d in research.values())
    print(f"\n{'='*50}")
    print(f"  MiMo v2.5 — Research Collection")
    print(f"{'='*50}")
    print(f"  Topics:    {len(research)}")
    print(f"  Sections:  {total_sections}")
    print(f"  Words:     {total_words:,}")
    print(f"{'='*50}\n")


def print_topics(research):
    """Print available topics."""
    print("\nAvailable topics:")
    for i, (key, data) in enumerate(research.items(), 1):
        print(f"  {i}. {data['title']} ({data['section_count']} sections, {data['word_count']:,} words)")
    print()


def browse_topic(research, key):
    """Browse a specific topic."""
    if key not in research:
        print(f"Topic '{key}' not found.")
        return
    
    data = research[key]
    print(f"\n{'='*50}")
    print(f"  {data['title']}")
    print(f"{'='*50}\n")
    
    for i, section in enumerate(data["sections"], 1):
        print(f"  {i}. {section['title']}")
    print()
    
    choice = input("Select section number (or Enter to go back): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(data["sections"]):
        section = data["sections"][int(choice) - 1]
        print(f"\n{'─'*50}")
        print(f"  {section['title']}")
        print(f"{'─'*50}\n")
        print(section["content"].strip())
        print()


def interactive_mode(research):
    """Run interactive browsing mode."""
    print_stats(research)
    
    while True:
        print("Commands: [l]ist topics, [b]rowse topic, [s]earch, [q]uit")
        cmd = input("> ").strip().lower()
        
        if cmd == "q" or cmd == "quit":
            print("Later.")
            break
        elif cmd == "l" or cmd == "list":
            print_topics(research)
        elif cmd == "b" or cmd == "browse":
            print_topics(research)
            choice = input("Topic number: ").strip()
            if choice.isdigit():
                keys = list(research.keys())
                if 1 <= int(choice) <= len(keys):
                    browse_topic(research, keys[int(choice) - 1])
        elif cmd == "s" or cmd == "search":
            query = input("Search query: ").strip()
            if query:
                results = search_research(research, query)
                if results:
                    print(f"\nFound {len(results)} matches:\n")
                    for r in results[:10]:
                        print(f"  [{r['topic']}] {r['section']}")
                        print(f"    {r['line'][:100]}...")
                        print()
                else:
                    print("No matches found.")
        else:
            print("Unknown command.")


def main():
    if not RESEARCH_DIR.exists():
        print(f"Research directory not found: {RESEARCH_DIR}")
        sys.exit(1)
    
    research = load_research()
    if not research:
        print("No research files found.")
        sys.exit(1)
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "stats":
            print_stats(research)
        elif cmd == "list":
            print_topics(research)
        elif cmd == "search" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            results = search_research(research, query)
            if results:
                print(f"Found {len(results)} matches:\n")
                for r in results:
                    print(f"  [{r['topic']}] {r['section']}")
                    print(f"    {r['line'][:120]}")
                    print()
            else:
                print("No matches found.")
        elif cmd in research:
            browse_topic(research, cmd)
        else:
            print(f"Unknown command or topic: {cmd}")
            print(f"Available topics: {', '.join(research.keys())}")
    else:
        interactive_mode(research)


if __name__ == "__main__":
    main()
