from recipes.models import User, models


class Follow(models.Model):
    """Модель для подписок на других пользователей."""
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        User,
        verbose_name='Подписка',
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(fields=['user', 'following'],
                                               name='unique_follow')]

    def __str__(self) -> str:
        return f'{self.user} - {self.following}'
