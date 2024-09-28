from click import Group

# From https://click.palletsprojects.com/en/8.1.x/advanced/#command-aliases
# Automatically "aliases" the cli-group's commands to any unique substring from start
class AliasedGroup(Group):
    def get_command(self, ctx, cmd_name):
        rv = Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args