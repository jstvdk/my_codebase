import marimo

__generated_with = "0.13.6"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return


@app.cell
def _():
    x = 3
    y = 5
    return (x,)


@app.cell
def _(x):
    print(x)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
