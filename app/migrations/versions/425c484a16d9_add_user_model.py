from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import expression

ORDER_STATUS_VALUES = ("PENDING", "PAID", "CANCELLED", "COMPLETED")
ORDER_STATUS_NAME = "orderstatus"
# revision identifiers, used by Alembic.
revision = "425c484a16d9"
down_revision = "c1c530ac8e1d"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # carts.is_active: проставим true существующим строкам и сделаем NOT NULL
    op.add_column(
        "carts",
        sa.Column("is_active", sa.Boolean(), server_default=expression.true(), nullable=False),
    )
    # (если не хочешь хранить дефолт дальше, можно сразу убрать)
    # op.alter_column("carts", "is_active", server_default=None)

    # 1) создать ENUM тип (если его ещё нет)
    bind = op.get_bind()
    order_status_enum = sa.Enum(*ORDER_STATUS_VALUES, name=ORDER_STATUS_NAME)
    order_status_enum.create(bind, checkfirst=True)

    # 2) нормализовать существующие текстовые значения
    op.execute("UPDATE orders SET status = UPPER(status) WHERE status IS NOT NULL")

    # 3) изменить тип колонки с USING-кастом
    op.alter_column(
        "orders",
        "status",
        type_=order_status_enum,
        existing_type=sa.VARCHAR(),
        postgresql_using=f"status::text::{ORDER_STATUS_NAME}",
        existing_nullable=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    order_status_enum = sa.Enum(*ORDER_STATUS_VALUES, name=ORDER_STATUS_NAME)

    # вернуть строковый тип
    op.alter_column(
        "orders",
        "status",
        type_=sa.VARCHAR(),
        existing_type=order_status_enum,
        postgresql_using="status::text",
        existing_nullable=False,
    )

    # удалить ENUM тип
    order_status_enum.drop(bind, checkfirst=True)

    # откатить carts.is_active
    op.drop_column("carts", "is_active")
