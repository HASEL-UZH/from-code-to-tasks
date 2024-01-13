export interface IObject {
    id: string;
    classifier: string;
    identifier: string;
}

export interface IStoreObject {
    _location?: string;
}

export interface IContainer extends IObject, IStoreObject {

}

export interface IRepository extends IContainer {
    identifier: string;
    repository_url: string;
}

/**
 * Commit Example
 * {
 *   "repository_url": "https:github.com/iluwatar/java-design-patterns",
 *   "commit_hash": "0ad44ced247191cc631100010ca40b4baa84d161",
 *   "commit_message": "docs: Fix typos spanish readme and factory (#1834)\n\n* Fix typos for Spanish README\r\n\r\n* Fix typos in the factory example",
 *   "pull_request": "Fix typos spanish readme and factory",
 *   "commit_author": "JCarlos",
 *   "committer_date": [15,10,2021]
 *   "commit_data": "2021-10-15"
 *   "in_main_branch": true,
 *   "merge": false,
 *   "added lines": 5,
 *   "deleted lines": 5
 *}
 */
export interface ICommit extends IContainer {
    "@repository": string;
    repository_url: string;
    commit_hash: string;
    commit_message: string;
    pull_request: string;
    commit_author: string;
    committer_date: [number, number, number];
    commit_date: string;
    in_main_branch: boolean;
    merge: boolean;
    added_lines: number;
    deleted_lines: number;
}

export interface IResource extends IObject, IStoreObject {
    "@container": string;
    identifier: string
    name: string;
    type: "json" | "diff" | "text"
    kind: "source" | "diff" | "ast" | "meta" | "change";
    version: "before" | "after" | null;
    strategy: {
        meta?: string;
        terms?: string;
        embedding?: string;
    }
    content: string | {} | any;
}





