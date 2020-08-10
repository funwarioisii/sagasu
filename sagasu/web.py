import streamlit as st

from sagasu.config import ConfigUtil
from sagasu.engine import SearchEngine

config = ConfigUtil().load()
search_engine = SearchEngine(config)


def main():
  st.title("sagasu")
  word = st.text_input('')
  resources = search_engine.word_search(word)
  if not resources and word:
    st.write(f"その単語は登録されていません")
  elif word and resources:
    resources = set(resources)
    md = ''.join(f"""
{resource.sentence[:200]}

{resource.uri}

---
""" for resource in resources)
    st.markdown(md)
  return


if __name__ == '__main__':
  main()
