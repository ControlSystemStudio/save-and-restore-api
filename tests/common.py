def _is_async(library):
    if library == "ASYNC":
        return True
    elif library == "THREADS":
        return False
    else:
        raise ValueError(f"Unknown library: {library!r}")
