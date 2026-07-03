# Gmail Setup for Manual Email Sending

This project keeps email sending behind an explicit human confirmation button in Streamlit. Without Gmail configuration, the Agent Workbench still generates and displays email drafts normally.

## 1. Create a Google Cloud Project and Enable Gmail API

1. Open Google Cloud Console.
2. Create a new project or select an existing project.
3. Enable the Gmail API for that project.

## 2. Create OAuth2 Client ID and Download credentials.json

1. Configure the OAuth consent screen.
2. Create an OAuth Client ID.
3. Choose `Desktop app` as the application type.
4. Download the credential file.
5. Rename it to:

```text
credentials.json
```

6. Put `credentials.json` in the project root directory.

Do not commit `credentials.json` to Git.

## 3. First Authorization Run

1. Start Streamlit:

```bash
streamlit run app_streamlit.py
```

2. Open the Agent Workbench tab.
3. Generate an email draft.
4. Enter recipient and subject.
5. Click the manual confirm send button.
6. The first run opens a browser for Google authorization.
7. After authorization succeeds, the project creates:

```text
token.json
```

Future sends reuse `token.json` and should not require reauthorization unless the token is revoked or expires without refresh.

Do not commit `token.json` to Git.

