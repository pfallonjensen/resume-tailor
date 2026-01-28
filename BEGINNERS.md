# Beginner's Guide: What Is This and Do I Need It?

## What is Claude Code?

Claude Code is a tool that lets you talk to an AI (Claude) directly from your computer's command line (that black window where you type commands). It's like ChatGPT, but it can read and edit files on your computer.

**Why use it instead of regular Claude/ChatGPT?**
- It can read your files directly (no copy-pasting)
- It can run code to validate things (like checking character counts)
- You can create "skills" - saved instructions for specific tasks

## What is this Resume Tailor skill?

It's a set of instructions and code that helps Claude:
1. Read a job description and find the important keywords
2. Compare those keywords to your resume
3. Suggest small edits to add missing keywords
4. **Crucially**: Only suggest words you've actually used before (no making stuff up)

## Do I need to be technical?

**Honest answer**: This tool requires some comfort with:
- Using Terminal (Mac) or Command Prompt (Windows)
- Installing software via command line
- Editing text files
- Basic file/folder navigation

If you've never used a command line before, expect a learning curve. It's not impossible, but budget 1-2 hours for setup.

## What do I need?

- A computer (Mac, Windows, or Linux)
- An Anthropic account (the company that makes Claude)
- ~30 minutes for initial setup
- Your resume and a job description to test with

## How to Install Claude Code

### Step 1: Install Node.js

Claude Code runs on Node.js. Download and install it:
- Go to https://nodejs.org
- Download the "LTS" version (the recommended one)
- Run the installer, click through the defaults

To verify it worked, open Terminal (Mac) or Command Prompt (Windows) and type:
```
node --version
```
You should see a version number like `v20.10.0`.

### Step 2: Install Claude Code

In Terminal/Command Prompt, type:
```
npm install -g @anthropic-ai/claude-code
```

Wait for it to finish (might take a minute).

### Step 3: Log in to Claude

Type:
```
claude
```

It will open a browser window to log in to your Anthropic account. Follow the prompts.

### Step 4: Verify it works

After logging in, you should see a prompt where you can type to Claude. Try:
```
> What's 2 + 2?
```

If Claude responds, you're set up!

## Next Steps

Once Claude Code is working:
1. Read the main [README.md](README.md) for how to set up the resume tailor skill
2. Look at the `users/fallon-jensen/` folder to see an example setup
3. Copy `users/_template/` and fill in your own files

## Still Confused?

**Option A**: Ask Fallon to walk you through it on a call

**Option B**: Use regular Claude.ai instead
- Go to claude.ai
- Create a Project
- Upload your resume and bullet corpus files
- Paste job descriptions and ask Claude to help tailor your resume
- (You won't get the automated validation, but you'll get 80% of the value)

**Option C**: Send Fallon your files and let him run it for you

No shame in any of these options. The goal is a better resume, not learning command-line tools.
