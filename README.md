# gitlab-portainer-deploy

## Usage

In `.gitlab-ci.yml`:

```yaml
deploy:
  stage: deploy
  image: vvarp/gitlab-portainer-deploy
  variables:
    PORTAINER_URL: ""
    PORTAINER_USERNAME: ""
    PORTAINER_PASSWORD: ""
    PORTAINER_STACK: ""
    STACKFILE: ""
  script:
    - deploy -e SOME_STACKFILE_VAR=value -e ANOTHER_STACKFILE_VAR=value
  tags:
    - docker
```
