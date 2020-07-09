# regaBOFH
regaBOFH - Slack deleter


----
## What is REGABOFH?
From the Portuguese word [regabofe](https://dicionario.priberam.org/regabofe) meaning party hard, this tool is the complete opposite. This will ruin [BOFH](https://en.wikipedia.org/wiki/Bastard_Operator_From_Hell) fun from enterprise slack admins by deleting your messages (including threaded messages), so they can't spy on you.

This tool will list all the private conversations (not the public ones or multiple user conversations). 
Then you can choose interactively which conversations you which to delete, for example; _friend1,friend2,..._
This will cache at the same time that backups your conversations in a [pickle](https://docs.python.org/3/library/pickle.html) format (we may want to run this multiple times and we should avoid hitting slack rate limit).

It will delete all your reactions.

And finally, it will backup your files (if you want) and delete them.

----
## Usage
1. Open slack on your browser and login on your workspace.
2. Open browser developer tool, by pressing F12 or any other way.

3. Go to the Network tab.

4. Select some HTTP request that contains the slack token (it will start with "xoxc-") and the cookies (I guess these don't need explanation).

5. Run the script without performing modifications on your account by adding **--dry-run** as argument (_It will print the messages like it is deleting, but it's not really requesting the deletion, it's only iterating the data_): 
  - **python3 slack.py --token <token_here> --cookie '<cookies_here>' --dry-run**

6. If it worked correctly and showed you the information, run the script without **--dry-run**:
  - **python3 slack.py --token <token_here> --cookie '<cookies_here>'**

WARNING: I take no responsibility for the effects of this tool, neither I control slack API. (During the development of this tool, reaction API got faulty, it may still faulty when you run this script).

----
## FAQ

Q. Will this permanently delete all messages?

A. Sort of... They are not displayed anymore on slack, but I guess slack organizations have ways to read them anyway. If Slack is self-hosted by your company they may have backups...

---

Q. Is it legal to delete messages and files? What about [DLP](https://en.wikipedia.org/wiki/Data_loss_prevention_software)?

A. Don't know. I take no responsibility for the use of this tool.

---

Q. Your code suck!!

A. I know it, but it does the job. deal with it. 

---

Q. Can't find the XOXC token we're talking about.

A. I don't know. Google it!

---

Q. Can you add X, Y, Z features?

A. I'm not feeling it, but you can send a pull request it of fork it to your profile.

---

Q. Will you add an option to delete public channels conversations or multiple users private conversations?

A. At the moment I don't feel the need for it. But how knows... Also, I'm available to accept pull requests.

---

Q. What's your open source license?

A. I don't give a F. do whatever you want. Feel free to include a credit if you like my tool. 

