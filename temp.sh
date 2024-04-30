# Get all authors
git --no-pager shortlog -sne
# Get all commits by author
git --no-pager log --author="David Belais <David.Belais@nike.com>"  --format=tformat: --numstat --since=