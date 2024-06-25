if test -f .venv/Scripts/activate
    source .venv/Scripts/activate
end

if test -f .venv/bin/activate.fish
    source .venv/bin/activate.fish
end

# source: https://gist.github.com/judy2k/7656bfe3b322d669ef75364a46327836
# usage: export_envs FILE
function export_envs
    set -l envFile (or $argv 1 .env)
    cat $envFile | while read -l line
        echo $line | grep -q '^[[:space:]]*#' && continue
        echo $line | grep -q '^[[:space:]]*$' && continue
        set -l key (echo $line | cut -d'=' -f1)
        set -l temp (echo $line | cut -d'=' -f2-)
        set -l value (eval echo $temp)
        set -x $key $value
    end
end

if test -f ".local/.env"
    export_envs .local/.env
end
