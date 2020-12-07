from .settings import Settings


class ModelsTests(Settings):
    def test_verbose_name(self):
        """Поле имеет верный verbose_name."""
        verboses = {
            'text': 'Текст',
            'group': 'Группа'
        }
        for field, name in verboses.items():
            with self.subTest(field=field, name=name):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    name, f'Проверьте verbose_text модели post поля {field}'
                    )

    def test_help_text(self):
        """Поле имеет верный help_text."""
        help_texts = {
            'text': 'Содержимое поста',
            'group': 'Куда разместить'
        }
        for field, text in help_texts.items():
            with self.subTest(field=field, text=text):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, text,
                    f'Проверьте help_text модели post поля {field}'
                    )

    def test_str_post(self):
        """Модель post имеет верное отображение."""
        post = self.post
        self.assertEqual(
            str(post), post.text[:15],
            'Проверьте работу def __str__ в post'
            )

    def test_str_group(self):
        """Модель group имеет верное отображение."""
        group = self.group
        self.assertEqual(
            str(group), group.title,
            'Проверьте работу def __str__ в group'
            )
