# Contributing to git-author-stats

## For Contributors and Code Owners

1. Clone and Install

    To install this project for development of *this library*,
    clone this repository (replacing "~/Code", below, with the directory
    under which you want your project to reside), then run `make`:

    ```bash
    cd ~/Code && \
    git clone\
    https://github.com/enorganic/git-author-stats.git\
    git-author-stats && \
    cd git-author-stats && \
    make
    ```

2. [Create a personal access token](https://bit.ly/46mVout), and create a
   `.env` file (in the project root) in which to store your token. It should
   look as follows (replacing "***" with the token you created):

   ```text
   GITHUB_TOKEN=***
   ```

3. Create a new branch for your changes (replacing "descriptive-branch-name"
   with a *descriptive branch name*, and replacing *feature* with *bugfix*
   if the branch addresses a bug):

    ```shell
    git branch feature/descriptive-branch-name
    ```

4. Make some changes.

5. Format and lint your code:

    ```shell
    make format
    ```

6. Test your changes:

    ```shell
    make test
    ```

7. Push your changes and create a pull request.

## For Everyone Else

If you are not a contributor on this project, you can still create pull
requests, however you will need to fork this project, push changes
to your fork, and create a pull request from your forked repository.
