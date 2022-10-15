import streamlit as st

st.set_page_config(page_title="markdownlit")

from markdownlit import mdlit

title = "# markdown[blue]lit[/blue]"
mdlit(title)

st.write("")


def mdlit_example(code: str) -> None:
    left, right = st.columns((2, 25))
    with left:
        mdlit("[gray]<small style='float:right'>In:</small>[/gray]")
    right.code(
        f"""mdlit("{code}")""",
        "python",
    )
    left, right = st.columns((2, 25))
    with left:
        mdlit("[gray]<small style='float:right'>Out:</small>[/gray]")
    with right:
        mdlit(code)


mdlit(
    f"""

#### Summary
markdownlit is a Markdown command in Python which puts together a few additional capabilities foreseen to be useful in the context of @(Streamlit)(streamlit.io) apps. It is built as an extension to the great @(https://github.com/Python-Markdown/markdown) project. You can use markdownlit along with `st.markdown()`!

Here are the features of markdownlit:

1. **Magic links** like @(🍐)(Pear)(https://www.youtube.com/watch?v=dQw4w9WgXcQ), @(https://youtube.com) @(twitter.com/arnaudmiribel), @(github.com/arnaudmiribel/streamlit-extras)
2. **Colored text.** Includes [red]red[/red], [green]green[/green], [blue]blue[/blue], [orange]orange[/orange] and [violet]violet[/violet].
3. ??? "**Collapsible content.** See this > toggle you're using right now!"
       Funny, right!
4. **Beautiful arrows.** Arrows - > are automatically translated to →
5. **Beautiful dashes.** Double dashes - - are automatically translated to —
"""
)

st.write("")
st.write("")

""" #### Get started!

Start by pip installing Markdownlit:

```
pip install markdownlit
```

To use it in your Streamlit app, simply add:

```python
from markdownlit import mdlit
```

In the top of your main Streamlit script and you can now call `mdlit()` instead of using the default `st.markdown()` from now on to benefit its Markdownlit additional capabilities! Hey, but what are these additional capabilities?
"""
st.write("")

"""
##### 1. Magic links

Markdownlit introduces a new operator `@()` to render links in a beautiful way!

For instance you can simply call `@(url)` with any given URL, and the method will look for the website's favicon and title so as to give it a nicer flavour.
"""

mdlit_example("""You should watch @(https://youtube.com/watch?v=dQw4w9WgXcQ)""")

"""
Twitter, Notion, Streamlit and GitHub links have dedicated parsers to improve yet again the labels!
"""
mdlit_example("""@(twitter.com/arnaudmiribel)""")

"""
You can also pass explicit parameters to the at sign so that you control the icon and the label of the link! For instance, if you're still tempted to trick people into watching Never Gonna Give You Up...
"""

mdlit_example("@(🎥)(Tutorial)(https://youtube.com/watch?v=dQw4w9WgXcQ)")

st.expander("See full documentation of @ operator").write(
    """
```markdown
@(icon)(label)(url*)
```
- icon (optional): Emoji character or link to an image (png/svg) or handle for some special cases e.g. 'github', 'streamlit', 'twitter'. If not specified, will get the favicon of the page.
- label (optional): Label of the link. If not specified, will get the title of the page.
- url* (mandatory): URL of the link.
"""
)
st.write("")
mdlit(
    """
##### 2. Colored text

Simply use `[color] foo [/color]` where color is red, green, blue, orange or violet.
"""
)

mdlit_example("I just came to say [violet] hello [/violet]")

st.write("")
mdlit(
    """
##### 3. Collapsible content
Taking advantage of @(https://github.com/facelessuser/pymdown-extensions/blob/main/pymdownx/details.py)'s existing Markdown extension:
"""
)

mdlit_example(
    """
??? "Click me!"
    Here's the secret
"""
)
