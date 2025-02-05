# Basedbot

A discord bot that lets people interact with powerful AI in a collaborative way.


### Setup
```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

### Running
```bash
./run dev # uses jurigged for hot reloading
./run prod 
```

### Development
```bash
pip3 freeze > requirements.txt
```

### Rsync Example
Running it on a remote server:

```bash
# a=preserve links, n=dry run, v=verbose
$ rsync -anv --exclude '.git/' . username@remote_host:/root/directory
# remove the `n` to run for real
```

You can run it with screen:
```bash
screen -S basedbot
./run prod
# ctrl+a+d to detach
# screen -r basedbot to reattach
```

### Notes
- Check Billing
<https://platform.openai.com/settings/organization/billing/overview>
- TODO: update dependencies once the discord audioop bug is fixed
