# Output formats

The fairness work is identical in every format.

| Use | Format |
|---|---|
| Quick self-test in the chat | Quiz widget (offers a flashcard view of the same questions) |
| A set the user keeps, redoes or shares (a Probeklausur) | Quiz artifact (self-contained HTML page) |
| Exercise inside a lesson page | The lesson's own components (teach: `./assets/`) |
| Printable exam or Musterlösung | Document or text, answer key separate from the questions |

**Quiz widget mapping**: each item gets `options` with short ids (`a` to `d`), a `correct_option_id`, an `explanation` (why the key is right and why the most tempting distractor is wrong), optionally a `hint`, and its own short `correct_feedback` and `incorrect_feedback`. Distribute correct positions yourself; the widget may shuffle but do not rely on it.

**Language**: questions follow the language of the course material; explanations follow the user's language (German for German-taught courses unless asked otherwise); established technical terms stay English.

**Recall cards** (term to definition) have few option tells; apply spoiler decoupling across the deck.
