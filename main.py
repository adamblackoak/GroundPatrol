from groundpatrol.agent import run


if __name__ == "__main__":
    print(
        run(
            "Patrol west-bay-01. Assess the debris situation. If an autonomous "
            "collection pass is cleared, create the bounded collection work order; "
            "otherwise stop or hand off safely and explain why."
        )
    )
