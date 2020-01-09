/*
    Copyright (c) 2006 Volker Krause <vkrause@kde.org>

    This library is free software; you can redistribute it and/or modify it
    under the terms of the GNU Library General Public License as published by
    the Free Software Foundation; either version 2 of the License, or (at your
    option) any later version.

    This library is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Library General Public
    License for more details.

    You should have received a copy of the GNU Library General Public License
    along with this library; see the file COPYING.LIB.  If not, write to the
    Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
    02110-1301, USA.
*/

#include "expungejob_p.h"

#include "job_p.h"

using namespace Akonadi;

class Akonadi::ExpungeJobPrivate : public JobPrivate
{
  public:
    ExpungeJobPrivate( ExpungeJob * parent )
      : JobPrivate( parent )
    {
    }
};

ExpungeJob::ExpungeJob(QObject * parent)
  : Job( new ExpungeJobPrivate( this ), parent )
{
}

ExpungeJob::~ExpungeJob()
{
}

void ExpungeJob::doStart()
{
  d_ptr->writeData( d_ptr->newTag() + " EXPUNGE\n" );
}

#include "expungejob_p.moc"
