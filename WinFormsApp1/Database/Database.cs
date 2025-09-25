using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WinFormsApp1.Models;

namespace WinFormsApp1;
public class Database : DbContext
{
    //public Database(DbContextOptions opts) : base(opts) { }

    protected override void OnConfiguring(DbContextOptionsBuilder options)
        => options.UseSqlite("Data Source=myapp.db");

    public DbSet<UserModel> users { get; set; }
}
