FROM mcr.microsoft.com/devcontainers/miniconda:3

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=0

USER root

RUN for attempt in 1 2 3 4; do \
        apt-get update && break; \
        echo "apt-get update failed, retrying in 20 seconds..." >&2; \
        sleep 20; \
    done \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        graphviz \
        libgl1 \
        libglib2.0-0 \
        patchelf \
        unzip \
    && rm -rf /var/lib/apt/lists/*

COPY .devcontainer/environment.yml /tmp/environment.yml

# PyTorch 1.12 wheels mark some ELF libraries as requiring an executable stack.
# Current Docker Desktop/WSL runtimes can reject that flag, so clear it after install.
RUN conda env create --file /tmp/environment.yml \
    && conda run --no-capture-output --name d2l python -m ipykernel install \
        --sys-prefix \
        --name d2l-pytorch \
        --display-name "Python (d2l-pytorch)" \
    && find /opt/conda/envs/d2l/lib/python3.9/site-packages/torch \
        -type f -name '*.so' -exec patchelf --clear-execstack '{}' + \
    && printf '%s\n' \
        '# Automatically activate the textbook environment in interactive Bash shells.' \
        'if [ -n "${PS1:-}" ] && [ -f /opt/conda/etc/profile.d/conda.sh ]; then' \
        '    . /opt/conda/etc/profile.d/conda.sh' \
        '    conda activate d2l >/dev/null 2>&1' \
        'fi' \
        >> /etc/bash.bashrc \
    && if [ -f /etc/zsh/zshrc ]; then \
        printf '%s\n' \
            '# Automatically activate the textbook environment in interactive Zsh shells.' \
            'if [[ -o interactive ]] && [ -f /opt/conda/etc/profile.d/conda.sh ]; then' \
            '    . /opt/conda/etc/profile.d/conda.sh' \
            '    conda activate d2l >/dev/null 2>&1' \
            'fi' \
            >> /etc/zsh/zshrc; \
    fi

ENV PATH=/opt/conda/envs/d2l/bin:/opt/conda/bin:${PATH} \
    CONDA_DEFAULT_ENV=d2l

WORKDIR /workspaces

EXPOSE 8888

CMD ["sleep", "infinity"]
