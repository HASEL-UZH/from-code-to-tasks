import re
from typing import Dict, Optional

def map_action_word(word: str, action_verbs_mapping: Dict[str, str]) -> Optional[str]:
    # Attempt to map the word or its subwords to an action verb
    for i in range(len(word), 0, -1):
        if word[:i] in action_verbs_mapping:
            return action_verbs_mapping[word[:i]]
    return None

def modify_issue(issue: str, action_verbs_mapping: Dict[str, str]) -> str:
    issue_words = issue.lower().split()
    first_word = issue_words[0]

    mapped_action_verb = map_action_word(first_word, action_verbs_mapping)
    if mapped_action_verb:
        issue_words[0] = mapped_action_verb

    task_label_issue = ' '.join(issue_words)
    cleaned_issue = re.sub(r'[^a-z\s]+', '', task_label_issue)

    print("Initial issue:", issue)
    print("Cleaned issue:", cleaned_issue)
    return cleaned_issue

if __name__ == '__main__':
    issue = "deleted xyz."
    action_verbs_mapping = {
        'code': 'create',
        'create': 'create',
        'define': 'create',
        'design': 'create',
        'implement': 'create',
        'insert': 'create',
        'make': 'create',
        'add': 'update',
        'adjust': 'update',
        'change': 'update',
        'edit': 'update',
        'extend': 'update',
        'fix': 'update',
        'improve': 'update',
        'insert': 'update',
        'renew': 'update',
        'replace': 'update',
        'refactor': 'update',
        'redesign': 'update',
        'bind': 'merge',
        'export': 'merge',
        'insert': 'merge',
        'integrate': 'merge',
        'invite': 'merge',
        'link': 'merge',
        'list': 'merge',
        'offer': 'merge',
        'delete': 'delete',
        'remove': 'delete',
        'check': 'validate',
        'evaluate': 'validate',
        'research': 'validate',
        'test': 'validate',
        'verify': 'validate',
        'accept': 'control',
        'allow': 'control',
        'apply': 'control',
        'bind': 'control',
        'cancel': 'control',
        'configure': 'control',
        'control': 'control',
        'determine': 'control',
        'inquire': 'investigate',
        'investigate': 'investigate',
        'research': 'investigate',
        'search': 'investigate'
    }
    modify_issue(issue, action_verbs_mapping)
