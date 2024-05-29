#!/usr/bin/env bash
# set -xe

cat <<EOF
workflow:
    rules:
        - when: always
EOF

# Recherche des challenges avec un Dockerfile, puis génère des jobs gitlab-ci

INCLUDES=("ci/jobs/.build-docker.gitlab-ci.yml")

CATEGORIES=("_exemple" "Crypto" "Reverse" "Web" "Pwn" "Misc" "Mobile" "Osint" "Forensic")

for category in ${CATEGORIES[@]}
do
    for folder in $category/*
    do
        # dockerfile=$(find ${folder} -name Dockerfile)
        challenge=$(basename ${folder})
        if [[ -f $folder/.gitlab-ci.yml ]]
        then
            INCLUDES+=("$folder/.gitlab-ci.yml")
#             cat <<EOF
# include: - $folder/.gitlab-ci.yml
# EOF
        else
            find $folder -name '*Dockerfile' | while read dockerfile
            do
                if [[ "$(basename $dockerfile)" == "Dockerfile" ]]
                then
                    image_name="${challenge,,}"
                else
                    dockerfile_filename="$(basename $dockerfile)"
                    image_name="${challenge,,}-${dockerfile_filename%.Dockerfile}"
                fi

            cat <<EOF
Build ${image_name}:
    extends: .build_docker
    variables:
        FOLDER: $(dirname ${dockerfile})
        DOCKERFILE: ${dockerfile}
        NAME: ${image_name}
    rules:
        - changes:
            - $(dirname ${dockerfile})/**/*
EOF

            done
        fi
    done
done

echo 'include:'
for include in ${INCLUDES[@]}
do
    echo "    - $include"
done

# C'est dégeulasse, mais gitlab n'accepte pas qu'il y ait des pipeline "vides"
# Ce job ne fait rien du tout et ne consomme rien du tout, mais ca règle le caprice de gitlab :')
cat <<EOF
Empty job:
    variables:
        GIT_STRATEGY: none
    script:
        - echo This job does nothing
EOF