# sagasu

Search from any resources(constructed by URI and sentence) in CLI.

let's `pip install sagasu`

## Requirements
 - python (>=3.8)
 - (Optional) Twitter Developer token and keys
    - need to crawl your favorite

## will support

looking for
  - [x] likes in Twitter
  - [ ] chat log in Slack
  - [x] pages in Scrapbox



# how to run
 1. `pip install sagasu`
 2. edit your config file
 3. (if you collect twitter info) set these environment variables
    - CONSUMER_KEY
    - CONSUMER_SECRET
    - ACCESS_TOKEN
    - ACCESS_TOKEN_SECRET
 4. `sagasu indexing`
 5. `sagasu search`
 
## image captioning(experimental)
if you enable caption feature, `sagasu` search any images.

`pip install sagasu[cation]`

and `SAGASU_CAPTION=true sagasu indexing`. 
 
 
## config file
Set `config.yml` under `$HOME/.sagasu/config`

```yaml
sources:
    - source_type: twitter
      target: <user name>
    - source_type: scrapbox
      target: <target project name>
```

## daemon

<details>
<summary>macOS</summary>

using launchd, set `example/me.funwarioisii.sagasu.plist` to `~/Library/LaunchAgents/me.funwarioisii.sagasu.plist`

`launchctl load ~/Library/LaunchAgents/me.funwarioisii.sagasu.plist`

</details>


# Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [cookiecutter-docker-science](https://docker-science.github.io/) project template.
