from django.db import models
from django.db.models import Q
from django.db.models import UniqueConstraint
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    slug = models.SlugField(null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, blank=True, related_name='liked_posts')
    pinned = models.BooleanField(default=False)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['pinned'], condition=Q(pinned=True),
                             name='unique_pinned')
        ]

    def __str__(self):
        return f'{self.author} created post: {self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    body = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f'{self.user} added a comment to post {self.post}'

    @property
    def children(self):
        return Comment.objects.filter(parent=self).reverse().select_related('user', 'parent')

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False
